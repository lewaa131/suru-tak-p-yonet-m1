__version__ = "0.9.1"

from kivy.config import Config

# Disable desktop mouse touch markers before Kivy initializes input providers.
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from datetime import date, timedelta
from pathlib import Path
from threading import Thread
import json
import sqlite3
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from app_popup import AppPopup as Popup
from kivy.lang import Builder
import theme
from kivy.uix.scrollview import ScrollView
from touch_scroll import TouchScrollView
from kivy.uix.spinner import Spinner
from mobile_ui import GreenSwitch as Switch
from text_entry import MobileTextInput as TextInput
from text_entry import TagNumberInput, DateInput
from herd import Herd, STATES, age_text, due_date, due_text, can_reproduce, reproduction_reason, parse_date
from portraits import CowPortrait
from portrait_model import portrait_caption
from photos import import_photo, remove_unused_photo
from registry import lookup, normalize_tag
from reminders import AndroidReminders, reminder_plan, load_settings, save_settings, DEFAULT_SETTINGS
from kivy.logger import Logger
from mobile_ui import big_button, Identity, AnimalCard, surface, NavButton, MetricCard
from dashboard import sections
from farm_settings import load_farm, save_farm, fresh_ids
from herd import card_status

GREEN = (.06,.42,.27,1)
INK = (.05,.25,.17,1)

def label(text, height=36, size=16, color=INK):
    w = Label(text=text,color=color,font_size=dp(size),size_hint_y=None,height=dp(height),halign='left',valign='middle')
    w.bind(size=lambda w,s:setattr(w,'text_size',(s[0],s[1])))
    return w

def button(text, action, height=56, variant='primary'):
    return big_button(text,action,height,variant)

def scroll_content(parent):
    scroll = TouchScrollView(do_scroll_x=False,bar_width=dp(3),scroll_timeout=350,scroll_distance=dp(10))
    body = BoxLayout(orientation='vertical',spacing=dp(12),size_hint_y=None,padding=[0,0,dp(4),0])
    body.bind(minimum_height=body.setter('height'))
    scroll.add_widget(body); parent.add_widget(scroll)
    return body

def human(day):
    return date.fromisoformat(day).strftime('%d.%m.%Y') if day else 'Bilinmiyor'

def paragraph(text):
    w = Label(text=text,color=INK,font_size=dp(15),size_hint_y=None,halign='left')
    w.bind(width=lambda w,v:setattr(w,'text_size',(v,None)),texture_size=lambda w,v:setattr(w,'height',v[1]+dp(12)))
    return w


def info_box(parent,title,tint=(1,1,1,1)):
    box = BoxLayout(orientation='vertical',spacing=dp(6),padding=dp(12),size_hint_y=None)
    box.bind(minimum_height=box.setter('height'))
    surface(box,tint,20)
    heading = paragraph(title)
    heading.bold = True
    heading.color = GREEN
    heading.font_size = dp(18)
    box.add_widget(heading)
    parent.add_widget(box)
    return box


def detail(box,title,value):
    caption = paragraph(title)
    caption.color = (.40,.47,.44,1)
    caption.font_size = dp(13)
    box.add_widget(caption)
    value_label = paragraph(str(value))
    box.add_widget(value_label)
    return value_label

class SuruApp(App):
    title = 'Sürüm · Sürü Takibi'

    def build(self):
        Window.clearcolor = (.94,.98,.95,1)
        Window.softinput_mode = '' if platform == 'android' else 'below_target'
        self.popup_stack = []
        self.herd = Herd(Path(self.user_data_dir)/'suru.sqlite3')
        self.farm_path = Path(self.user_data_dir)/'farm-settings.json'
        self.farm = load_farm(self.farm_path)
        self.reminder_settings_path = Path(self.user_data_dir)/'reminder-settings.json'
        try:
            self.reminder_settings = load_settings(self.reminder_settings_path)
        except (OSError,ValueError,KeyError,TypeError):
            Logger.exception('Surum: Bildirim ayarları okunamadı')
            self.reminder_settings = dict(DEFAULT_SETTINGS)
        self.reminders = None
        self.reminder_error = ''
        if platform == 'android':
            try:
                self.reminders = AndroidReminders()
            except Exception:
                Logger.exception('Surum: Bildirim sistemi başlatılamadı')
                self.reminder_error = 'Bildirim sistemi açılamadı.'
        self.base = BoxLayout(orientation='vertical',padding=dp(12),spacing=dp(10))
        with self.base.canvas.before:
            Color(.94,.98,.95,1)
            background = Rectangle(pos=self.base.pos,size=self.base.size)
        self.base.bind(pos=lambda w,p:setattr(background,'pos',p),size=lambda w,s:setattr(background,'size',s))
        self.current_id = self.editor = self.camera_popup = None
        self.closed = False
        self.display_day = date.today()
        self.tab = 'herd'
        self.shell = BoxLayout(orientation='vertical')
        self.shell.add_widget(self.base)
        self.nav = BoxLayout(size_hint_y=None,height=dp(72),padding=[dp(6),dp(4),dp(6),dp(6)],spacing=dp(3))
        surface(self.nav,(1,1,1,1),0)
        self.nav_buttons = {}
        for key,title in [('herd','Sürüm'),('today','Bugün'),('special','Özel'),('archive','Arşiv')]:
            nav_button = NavButton(key,title,lambda _,key=key:self.open_tab(key))
            self.nav_buttons[key] = nav_button
            self.nav.add_widget(nav_button)
        self.shell.add_widget(self.nav)
        self.query, self.selection = '', 'Tüm hayvanlar'
        self.home()
        Clock.schedule_interval(self.tick,60)
        Window.bind(on_keyboard=self.keyboard)
        return self.shell

    def tick(self,*_):
        if self.closed or self.editor or date.today() == self.display_day: return
        self.display_day = date.today()
        self.sync_reminders()
        scroll = next((w for w in self.base.children if isinstance(w,ScrollView)),None)
        position = scroll.scroll_y if scroll else 1
        if self.current_id is None:
            if self.tab == 'herd': self.refresh()
            else: self.grouped_home()
        elif not self.editor: self.profile(self.current_id)
        def restore(*_):
            scroll = next((w for w in self.base.children if isinstance(w,ScrollView)),None)
            if scroll: scroll.scroll_y = position
        Clock.schedule_once(restore)

    def keyboard(self,window,key,*args):
        if key in (27, 1001): return self.go_back()
        return False

    def go_back(self):
        active = self.popup_stack[-1] if self.popup_stack else self.shell
        for widget in active.walk():
            if isinstance(widget, TextInput) and widget.focus:
                widget.focus = False
                return True
        for widget in active.walk():
            if isinstance(widget, Spinner) and widget.is_open:
                widget.is_open = False
                return True
        if self.popup_stack:
            self.popup_stack[-1].dismiss()
            return True
        if self.current_id is not None:
            self.home()
            return True
        if self.tab != 'herd':
            self.open_tab('herd')
            return True
        return False

    def dialog(self,title):
        # Forms replace each other; never leave another form and its Cancel
        # button underneath. Notices may still temporarily cover a form.
        for previous in list(self.popup_stack):
            previous.dismiss(animation=False)
        layout = BoxLayout(orientation='vertical',padding=dp(8),spacing=dp(8))
        body = scroll_content(layout)
        error = label('',0,14,(.65,.20,.12,1))
        error.bind(text=lambda w,t:setattr(w,'height',dp(72) if t else 0)); layout.add_widget(error)
        actions = BoxLayout(orientation='vertical',size_hint_y=None,spacing=dp(10))
        actions.bind(minimum_height=actions.setter('height')); layout.add_widget(actions)
        popup = Popup(title=title,content=layout,size_hint=(.96,.94),auto_dismiss=False,
                      title_size=dp(20))
        popup.is_editor = True
        self.editor = popup
        def dismissed(*_):
            if self.editor is popup:
                self.editor = next((p for p in reversed(self.popup_stack)
                                    if p is not popup and getattr(p,'is_editor',False)),None)
        popup.bind(on_dismiss=dismissed)
        cancel = button('Vazgeç',lambda *_:None,variant='secondary')
        # Close on press, before Android hiding the keyboard can move the
        # button away from the finger and cancel its release event.
        cancel.bind(on_press=lambda *_:popup.dismiss(animation=False))
        actions.add_widget(cancel)
        popup.open()
        return popup,body,error,actions

    def field(self,body,title,text='',multiline=False,max_length=None,date_input=False):
        body.add_widget(label(title,32,14,INK))
        entry = (DateInput if date_input else TextInput)(text=str(text),multiline=multiline,size_hint_y=None,height=dp(104 if multiline else 56),font_size=dp(16),padding=[dp(12),dp(14)])
        if max_length is not None:
            def limit_text(widget,value):
                if len(value) > max_length:
                    cursor = min(widget.cursor_index(),max_length)
                    widget.text = value[:max_length]
                    widget.cursor = widget.get_cursor_from_index(cursor)
            entry.bind(text=limit_text)
            limit_text(entry,entry.text)
        body.add_widget(entry)
        return entry

    def notice(self,text):
        box = BoxLayout(orientation='vertical',padding=dp(12),spacing=dp(10))
        box.add_widget(label(text,140,16,INK))
        popup = Popup(title='Bilgi',content=box,size_hint=(.9,None),height=dp(330))
        box.add_widget(button('Tamam',lambda *_:popup.dismiss()))
        popup.open()

    def home(self,*_):
        for key,nav_button in self.nav_buttons.items(): nav_button.select(key==self.tab)
        if self.tab != 'herd':
            self.grouped_home(); return
        self.current_id = None
        self.base.clear_widgets()
        header = BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(12))
        heading = label('Benim sürüm',48,26)
        heading.bold = True
        header.add_widget(heading)
        settings = button('Ayarlar',lambda *_:self.farm_options(),48,variant='secondary')
        settings.size_hint_x=None; settings.width=dp(88)
        header.add_widget(settings); self.base.add_widget(header)
        body = scroll_content(self.base)
        hero = BoxLayout(orientation='vertical',padding=dp(20),size_hint_y=None,height=dp(118))
        surface(hero,(.04,.33,.22,1),22)
        hero.add_widget(label('ÇİFTLİĞİM',24,12,(.69,.91,.75,1)))
        self.summary = label('',48,25,(1,1,1,1)); self.summary.bold=True
        hero.add_widget(self.summary)
        hero.add_widget(label('Her hayvan, ayrı bir hikâye.',22,13,(.80,.94,.84,1)))
        body.add_widget(hero)
        self.metrics = {}
        specs = [('Sağmallar','Sağmal','milk','mint'),('Gebeler','Gebe','birth','blue'),
                 ('Kurular','Kuruda','dry','coral'),('Tohumlananlar','Tohumlandı','seed','violet'),
                 ('Tazeler','Yeni doğuran','herd','mint'),('Yaklaşan / tarihi geçen doğumlar','Doğum takibi','special','coral')]
        for offset in range(0,len(specs),2):
            row = BoxLayout(size_hint_y=None,height=dp(114),spacing=dp(12))
            for key,title,kind,tone in specs[offset:offset+2]:
                card = MetricCard(title,0,kind,tone,lambda _,key=key:self.select_metric(key))
                self.metrics[key]=card; row.add_widget(card)
            body.add_widget(row)
        body.add_widget(label('İneklerim',36,22))
        self.search = TextInput(text=self.query,hint_text='İsim veya küpe ara',multiline=False,size_hint_y=None,height=dp(56),font_size=dp(17),padding=[dp(14),dp(15)])
        body.add_widget(self.search)
        self.filter = Spinner(text=self.selection,values=('Tüm hayvanlar','Dişiler','Erkekler','Sağmallar','Gebeler','Kurular','Tohumlananlar','Tazeler','Yaklaşan / tarihi geçen doğumlar'),size_hint_y=None,height=dp(52),font_size=dp(14),background_normal='',background_color=GREEN,sync_height=True)
        body.add_widget(self.filter)
        self.cards = BoxLayout(orientation='vertical',spacing=dp(12),size_hint_y=None)
        self.cards.bind(minimum_height=self.cards.setter('height')); body.add_widget(self.cards)
        self.home_scroll = body.parent
        self.base.add_widget(button('+  Hayvan ekle',lambda *_:self.add_animal()))
        self.search.bind(text=lambda *_:self.refresh())
        self.filter.bind(text=lambda *_:self.refresh())
        self.refresh()
        self.sync_reminders()

    def sync_reminders(self,force=False):
        if self.closed: return
        if self.reminders:
            try:
                self.reminders.sync(self.herd.all(),force=force,settings=self.reminder_settings)
                self.reminder_error = ''
            except Exception:
                Logger.exception('Surum: Hatırlatmalar güncellenemedi')
                self.reminder_error = 'Hatırlatmalar güncellenemedi. Uygulamayı yeniden aç.'
        if hasattr(self,'notification_status'):
            self.notification_status.text = self.reminder_state()

    def reminder_state(self):
        if self.reminder_error: return 'Kontrol gerekli'
        if self.reminders is None: return 'Android’de bildirim'
        try:
            return 'Açık' if self.reminders.enabled() else 'İzin kapalı'
        except Exception:
            return 'Kontrol gerekli'

    def request_notifications(self,manual=False):
        if not self.reminders: return
        try:
            if self.reminders.enabled():
                self.sync_reminders(); return
            marker = Path(self.user_data_dir)/'notification-permission-requested'
            from jnius import autoclass
            if autoclass('android.os.Build$VERSION').SDK_INT >= 33 and not marker.exists():
                from android.permissions import request_permissions
                marker.touch()
                def result(*_):
                    Clock.schedule_once(lambda _:self.sync_reminders())
                request_permissions(['android.permission.POST_NOTIFICATIONS'],result)
            elif manual:
                self.reminders.settings()
        except Exception:
            Logger.exception('Surum: Bildirim izni açılamadı')
            self.notice('Bildirim izni açılamadı. Telefon ayarlarından Sürüm bildirimlerini aç.')

    def reminder_options(self):
        popup,body,error,actions = self.dialog('Bildirim ayarları')
        days = self.field(body,'Kuruya ayır · kaç gün önce?',self.reminder_settings['dry_days'])
        days.input_filter = 'int'; days.input_type = 'number'
        clock = self.field(body,'Bildirim saati',self.reminder_settings['time'])
        clock.hint_text = '09:00'
        def save(*_):
            try:
                self.reminder_settings = save_settings(self.reminder_settings_path,days.text.strip(),clock.text.strip())
            except (ValueError,OSError) as exc:
                error.text = str(exc); return
            self.sync_reminders(force=True)
            if self.reminder_error:
                error.text = self.reminder_error; return
            popup.dismiss()
            if self.current_id is not None: self.profile(self.current_id)
            else: self.home()
            self.request_notifications(manual=True)
        actions.add_widget(button('Kaydet',save))

    def refresh(self):
        if self.current_id is not None: return
        cows = sections(self.herd.all(),'herd')[0][1]
        self.query,self.selection = self.search.text,self.filter.text
        soon = lambda c: due_date(c) is not None and (due_date(c)-date.today()).days <= 30
        self.summary.text = f'{len(cows)} hayvan'
        fresh = fresh_ids(self.herd,cows,self.farm['fresh_days'])
        predicates = {
            'Sağmallar':lambda c:c['state']=='Sağmal',
            'Gebeler':lambda c:can_reproduce(c) and bool(c['pregnant']),
            'Kurular':lambda c:c['state']=='Kuru dönemde',
            'Tohumlananlar':lambda c:can_reproduce(c) and bool(c['insemination']) and not c['pregnant'],
            'Tazeler':lambda c:c['id'] in fresh,
            'Yaklaşan / tarihi geçen doğumlar':soon}
        for key,card in self.metrics.items(): card.value.text=str(sum(bool(predicates[key](c)) for c in cows))
        self.cards.clear_widgets()
        rows = [c for c in cows if self.query.strip().casefold() in (c['tag']+' '+c['name']).casefold()]
        if self.selection in ('Dişiler','Erkekler'):
            rows = [c for c in rows if c['sex'] == ('Dişi' if self.selection=='Dişiler' else 'Erkek')]
        elif self.selection in predicates: rows = [c for c in rows if predicates[self.selection](c)]
        rows.sort(key=lambda c:(due_date(c) or date.max,c['tag']))
        if not rows: self.cards.add_widget(label('Sürünü oluşturmaya başla.\n+ Hayvan ekle' if not cows else 'Eşleşen hayvan bulunamadı.',90))
        for cow in rows:
            text = cow['state'] + (' · Gebe' if cow['pregnant'] and can_reproduce(cow) else ' · Tohumlandı' if cow['insemination'] and can_reproduce(cow) else '')
            if due_date(cow): text += '\n'+due_text(cow)
            self.cards.add_widget(AnimalCard(cow,self.portrait(cow),text,lambda _,i=cow['id']:self.profile(i)))

    def select_metric(self,key):
        self.search.text = ''
        self.filter.text = key
        def reveal(_):
            available = self.home_scroll.children[0].height-self.home_scroll.height
            self.home_scroll.scroll_y = max(0,min(1,(self.cards.height-self.home_scroll.height)/available)) if available > 0 else 1
        Clock.schedule_once(reveal,.1)

    def farm_options(self):
        from settings_ui import open_cycle_settings
        return open_cycle_settings(self)

    def active_farm_options(self):
        popup,body,error,actions = self.dialog('Çiftlik ayarları')
        duration = self.field(body,'Yeni kayıt · gebelik günü',self.farm['gestation_days'])
        fresh = self.field(body,'Yeni doğuran · kaç gün?',self.farm['fresh_days'])
        body.add_widget(label('Mevcut gebelik tarihleri korunur.',48,14,INK))
        def save(*_):
            try:
                values = {'gestation_days':duration.text,'fresh_days':fresh.text}
                self.farm = save_farm(self.farm_path,values)
            except (ValueError,OSError) as exc:
                error.text=str(exc); return
            popup.dismiss(); self.home()
        actions.add_widget(button('Kaydet',save))
        def notifications(*_):
            popup.dismiss(); self.reminder_options()
        actions.add_widget(button('Bildirim · gün ve saat',notifications,variant='secondary'))

    def open_tab(self,key):
        if self.editor: self.editor.dismiss()
        self.tab = key
        self.home()

    def grouped_home(self):
        self.current_id = None
        self.base.clear_widgets()
        titles = {'today':'BUGÜN','birth':'DOĞUM','special':'ÖZEL DURUM','archive':'ARŞİV'}
        self.base.add_widget(label(titles[self.tab],42,26))
        body = scroll_content(self.base)
        for title,rows in sections(self.herd.all(),self.tab,dry_days=self.reminder_settings['dry_days']):
            group = info_box(body,f'{title} · {len(rows)}')
            if not rows: group.add_widget(paragraph('Kayıt yok.'))
            for cow in rows:
                card = info_box(group,cow['name'] or cow['tag'],(.88,.95,.90,1))
                if cow['name']: card.add_widget(paragraph(cow['tag']))
                if self.tab == 'archive':
                    card.add_widget(paragraph(human(cow['status_date'])))
                else:
                    card.add_widget(paragraph(due_text(cow) if due_date(cow) else cow['state']))
                card.add_widget(button('Profili aç',lambda _,i=cow['id']:self.profile(i),48,variant='secondary'))
                if self.tab == 'archive':
                    card.add_widget(button('Sürüye geri al',lambda _,i=cow['id']:self.record_action(i,'Aktif'),48,variant='secondary'))
                else:
                    due = due_date(cow)
                    if due and due <= date.today():
                        card.add_widget(button('Doğum yaptı',lambda _,i=cow['id']:self.record_action(i,'Doğum yaptı'),48))
                    elif due and cow['state'] != 'Kuru dönemde':
                        card.add_widget(button('Kuruya ayırdım',lambda _,i=cow['id']:self.record_action(i,'Kuruya ayrıldı'),48))
        self.sync_reminders()

    def record_action(self,cow_id,action):
        cow = self.herd.get(cow_id)
        popup,body,error,actions = self.dialog('Sürüye geri al' if action=='Aktif' else action)
        identity = paragraph(f'{cow["name"] or "Hayvanım"} · {cow["tag"]}')
        identity.color = INK; body.add_widget(identity)
        messages = {
            'Satıldı':'Satılanlar listesine taşınır. Kayıtlar korunur.',
            'Öldü':'Ölenler listesine taşınır. Kayıtlar korunur.',
            'Arşiv':'Arşivlenenler listesine taşınır. Bildirimler kapanır.',
            'Aktif':'Aktif sürüye döner. Gebelik kaydı varsa bildirimler yeniden açılır.',
            'Doğum yaptı':'Gebelik kapanır, durum Sağmal olur. Doğum tarihi saklanır.',
            'Kuruya ayrıldı':'Durum Kuru dönemde olur. Doğum bildirimi devam eder.'}
        message = paragraph(messages[action]); message.color = INK; body.add_widget(message)
        day = self.field(body,'İşlem tarihi',date.today().strftime('%d.%m.%Y'),date_input=True)
        def save(*_):
            try:
                if action=='Doğum yaptı': self.herd.record_birth(cow_id,day.text)
                elif action=='Kuruya ayrıldı': self.herd.mark_dry(cow_id,day.text)
                else: self.herd.move_record(cow_id,action,day.text)
            except (ValueError,sqlite3.Error) as exc:
                error.text = str(exc); return
            popup.dismiss()
            if self.current_id is not None: self.profile(cow_id)
            else: self.home()
        actions.add_widget(button('Onayla',save))

    def portrait(self,cow):
        if cow['photo_path'] and Path(cow['photo_path']).is_file(): return Image(source=cow['photo_path'],fit_mode='contain')
        return CowPortrait(cow)

    def add_animal(self):
        popup,body,error,actions = self.dialog('Hayvan ekle')
        body.add_widget(label('Küpeyi gir. Bilgiler gelsin.',80,17,INK))
        body.add_widget(label('Küpe · 12 rakam',32,14,INK))
        tag_row = BoxLayout(size_hint_y=None,height=dp(64),spacing=dp(8))
        prefix = label('TR',64,20,(1,1,1,1))
        prefix.size_hint_x = None; prefix.width = dp(54); prefix.halign = 'center'
        surface(prefix,GREEN,12)
        tag_row.add_widget(prefix)
        entry = TagNumberInput(hint_text='350004339192',font_size=dp(16),padding=[dp(12),dp(14)])
        tag_row.add_widget(entry); body.add_widget(tag_row)
        fetch_button = button('Bilgileri getir',lambda *_:start()); actions.add_widget(fetch_button)
        def start():
            try:
                if len(entry.text) != 12:
                    raise ValueError('Küpe numarası 12 rakam olmalı.')
                tag = normalize_tag('TR'+entry.text)
                if any(c['tag'].upper()==tag for c in self.herd.all()): raise ValueError('Bu küpe numarası zaten kayıtlı.')
            except ValueError as exc: error.text = str(exc); return
            fetch_button.disabled = entry.disabled = True
            error.text = 'Sorgulanıyor…'
            self.fetch(tag,finished)
        def finished(info,message):
            if self.editor is not popup: return
            error.text = message or ''
            if info is None:
                fetch_button.disabled = entry.disabled = False; return
            body.clear_widgets()
            body.add_widget(label(f'{info["tag"]}\n{info["species"]} · {info["sex"]}\n{info["breed"]}\nDoğum: {human(info["born"])}\nResmi durum: {info["registry_status"]}',180,18,INK))
            body.add_widget(label('Kontrol et. Sürüne ekle.',48,15,INK))
            actions.remove_widget(fetch_button)
            def save(*_):
                try: cow_id = self.herd.register(info,gestation_days=self.farm['gestation_days'])
                except (ValueError,sqlite3.Error) as exc: error.text = str(exc); return
                popup.dismiss(); self.profile(cow_id)
            actions.add_widget(button('Sürüme ekle',save))

    def fetch(self,tag,done):
        def deliver(info,message):
            if not self.closed: done(info,message)
        def work():
            try: info,message = lookup(tag),None
            except Exception as exc: info,message = None,str(exc) if isinstance(exc,ValueError) else 'Sorgulama tamamlanamadı. Tekrar deneyin.'
            if not self.closed: Clock.schedule_once(lambda _:deliver(info,message))
        Thread(target=work,daemon=True).start()

    def profile(self,cow_id):
        self.sync_reminders()
        cow = self.herd.get(cow_id); self.current_id = cow_id
        self.base.clear_widgets(); self.base.add_widget(button('‹ Listeye dön',self.home,48,variant='secondary'))
        body = scroll_content(self.base)
        body.spacing = dp(12)
        identity = info_box(body,'KİMLİK')
        identity.add_widget(Identity(cow))
        portrait = self.portrait(cow)
        portrait.size_hint_y = None; portrait.height = dp(120)
        identity.add_widget(portrait)
        caption = 'Kendi fotoğrafın' if cow['photo_path'] and Path(cow['photo_path']).is_file() else portrait_caption(cow)
        if cow['photo_path']: identity.add_widget(paragraph(caption))
        detail(identity,'Cinsiyet · Irk',f'{cow["sex"]} · {cow["breed"] or "Irk bilinmiyor"}')
        detail(identity,'Doğum · Yaş',f'{human(cow["born"])} · {age_text(date.fromisoformat(cow["born"]))}')
        detail(identity,'Tür',cow['species'] or 'Bilinmiyor')
        identity.add_widget(button('Fotoğrafı değiştir',lambda *_:self.photo_options(cow_id),variant='secondary'))

        care = info_box(body,'DURUM VE BAKIM')
        detail(care,'Durum',cow['state'] + (' · Gebe' if cow['pregnant'] and can_reproduce(cow) else ''))
        if cow['record_status'] != 'Aktif': detail(care,'Arşiv durumu',cow['record_status'])
        detail(care,'Notlar',cow['notes'] or 'Not yok.')
        care.add_widget(button('Profili düzenle',lambda *_:self.care(cow_id),variant='secondary'))

        reproduction = info_box(body,'GEBELİK',(.90,.95,.91,1))
        due = due_date(cow)
        if can_reproduce(cow):
            detail(reproduction,'Son tohumlama',human(cow['insemination']))
            detail(reproduction,'Gebelik durumu',due_text(cow))
            reproduction.add_widget(button('Tohumlama ve gebelik',lambda *_:self.reproduction(cow_id)))
            if cow['pregnant']:
                reproduction.add_widget(button('Doğum yaptı',lambda *_:self.record_action(cow_id,'Doğum yaptı'),variant='secondary'))
                if due and cow['state'] != 'Kuru dönemde':
                    reproduction.add_widget(button('Kuruya ayırdım',lambda *_:self.record_action(cow_id,'Kuruya ayrıldı'),variant='secondary'))
        else:
            reproduction.add_widget(paragraph(reproduction_reason(cow)))

        reminders = info_box(body,'HATIRLATMALAR')
        if due:
            dry = 'Kuru dönemde' if cow['state']=='Kuru dönemde' else human((due-timedelta(days=self.reminder_settings['dry_days'])).isoformat())
            detail(reminders,'Kuruya ayır',dry)
            detail(reminders,'Tahmini doğum',human(due.isoformat()))
        else:
            reminders.add_widget(paragraph('Aktif doğum hatırlatması yok.'))
        self.notification_status = detail(reminders,'Bildirimler',self.reminder_state())
        reminders.add_widget(button('Bildirim ayarları',lambda *_:self.reminder_options(),variant='secondary'))

        history_box = info_box(body,'TOHUMLAMA GEÇMİŞİ')
        history = self.herd.history(cow_id)
        if not history:
            history_box.add_widget(paragraph('Henüz kayıt yok.'))
        for day in history:
            row = BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(8))
            row.add_widget(label(human(day),48))
            remove = button('×',lambda _,day=day:self.delete_insemination(cow_id,day),48,variant='danger')
            remove.size_hint_x = None; remove.width = dp(48)
            row.add_widget(remove)
            history_box.add_widget(row)

        vaccine_box = info_box(body,'AŞI KAYITLARI')
        vaccines = json.loads(cow['vaccinations'])
        if not vaccines:
            vaccine_box.add_widget(paragraph('Aşı kaydı yok.'))
        for vaccine in vaccines:
            detail(vaccine_box,human(vaccine['date']),vaccine['group'])

        official = info_box(body,'RESMİ BİLGİLER')
        detail(official,'Resmi durum',cow['registry_status'] or 'Bilinmiyor')
        detail(official,'Son sorgu',cow['checked_at'].replace('T',' ') or 'Henüz sorgulanmadı')
        sync_button = button('Bilgileri yenile',lambda *_:sync(),variant='secondary')
        official.add_widget(sync_button)
        status = paragraph('')
        status.bind(text=lambda w,t:setattr(w,'opacity',1 if t else 0))
        official.add_widget(status)

        manage = info_box(body,'KAYIT İŞLEMLERİ',(.91,.96,.91,1))
        if cow['record_status']=='Aktif':
            for title in ('Satıldı','Öldü','Arşiv'):
                manage.add_widget(button(title,lambda _,title=title:self.record_action(cow_id,title),variant='secondary'))
        else:
            manage.add_widget(button('Sürüye geri al',lambda *_:self.record_action(cow_id,'Aktif'),variant='secondary'))
        events = self.herd.events(cow_id)
        if events:
            for event in events: manage.add_widget(paragraph(f'{human(event["day"])} · {event["kind"]}'))
        manage.add_widget(button('Hayvanı sil',lambda *_:self.delete_animal(cow_id),variant='danger'))
        def sync():
            sync_button.disabled = True; status.text = 'Sorgulanıyor…'
            def finished(info,message):
                if self.current_id!=cow_id or status.get_root_window() is None: return
                if info is None: status.text = message; sync_button.disabled = False; return
                try: self.herd.sync(cow_id,info)
                except (ValueError,sqlite3.Error) as exc: status.text = str(exc); sync_button.disabled = False; return
                self.profile(cow_id)
            self.fetch(cow['tag'],finished)

    def delete_insemination(self,cow_id,day):
        cow = self.herd.get(cow_id)
        popup,body,error,actions = self.dialog('Tohumlama kaydı silinsin mi?')
        text = f'{cow["name"] or cow["tag"]}\n{human(day)} tarihli kayıt silinecek.'
        if cow['insemination'] == day:
            text += '\n\nBu tarih aktif tohumlama kaydı. Gebelik işareti ve buna bağlı doğum/kuruya ayırma hatırlatmaları da kaldırılacak.'
        body.add_widget(paragraph(text))
        def confirm(*_):
            try: self.herd.delete_insemination(cow_id,day)
            except (ValueError,sqlite3.Error) as exc:
                error.text = str(exc); return
            popup.dismiss()
            self.profile(cow_id)
        actions.add_widget(button('Evet, sil',confirm,variant='danger'))

    def delete_animal(self,cow_id):
        cow = self.herd.get(cow_id)
        popup,body,error,actions = self.dialog('Hayvanı sil')
        message = paragraph(
            f'{cow["name"] or "İsimsiz hayvan"}\nKüpe: {cow["tag"]}\n\n'
            'Hayvan ve tüm geçmişi silinecek. '
            'Geri alınamaz. Resmi kayıtlar değişmez.'
        )
        message.color = INK
        body.add_widget(message)
        def confirm(*_):
            try:
                self.herd.delete(cow_id)
            except (ValueError,sqlite3.Error) as exc:
                error.text = str(exc); return
            popup.dismiss()
            self.cleanup_photo(cow['photo_path'])
            self.home()
        delete_button = button('Evet, sil',confirm,variant='danger')
        actions.add_widget(delete_button)

    def care(self,cow_id):
        cow = self.herd.get(cow_id)
        popup,body,error,actions = self.dialog('Bakım bilgileri')
        name = self.field(body,'İsim (isteğe bağlı)',cow['name'])
        values = STATES if cow['sex']=='Dişi' else ('Buzağı','Diğer')
        body.add_widget(label('Durum',32,14,INK))
        state = Spinner(text=cow['state'] if cow['state'] in values else 'Diğer',values=values,size_hint_y=None,height=dp(64),font_size=dp(18),sync_height=True); body.add_widget(state)
        notes = self.field(body,'Bakım ve sağlık notları',cow['notes'],True)
        def save(*_):
            try: self.herd.update_care(cow_id,name.text,state.text,notes.text)
            except (ValueError,sqlite3.Error) as exc: error.text = str(exc); return
            popup.dismiss(); self.profile(cow_id)
        actions.add_widget(button('Kaydet',save))

    def reproduction(self,cow_id):
        cow = self.herd.get(cow_id)
        if not can_reproduce(cow): self.notice(reproduction_reason(cow)); return
        popup,body,error,actions = self.dialog('Tohumlama ve gebelik')
        day = self.field(body,'Son tohumlama · gün.ay.yıl',human(cow['insemination']) if cow['insemination'] else '',date_input=True)
        duration = self.field(body,'Tahmini gebelik süresi (gün)',cow['gestation_days'])
        line = BoxLayout(size_hint_y=None,height=dp(64)); line.add_widget(Label(text='Gebelik doğrulandı',color=INK))
        pregnant = Switch(active=bool(cow['pregnant'])); line.add_widget(pregnant); body.add_widget(line)
        preview = label('',90,15,INK); body.add_widget(preview)
        def prediction(*_):
            try:
                due = parse_date(day.text)+timedelta(days=int(duration.text))
                preview.text = f'Tahmini doğum:\n{due:%d.%m.%Y}\nTarih tahminidir.'
            except (ValueError,OverflowError): preview.text = 'Tarih gir. Tahmini doğumu gör.'
        day.bind(text=prediction); duration.bind(text=prediction); prediction()
        body.add_widget(label('Doğum olduysa tarihi temizle, gebeliği kapat.\nGeçmiş korunur.',80,14,INK))
        def save(*_):
            try: self.herd.update_reproduction(cow_id,day.text,pregnant.active,duration.text)
            except (ValueError,sqlite3.Error) as exc: error.text = str(exc); return
            popup.dismiss(); self.profile(cow_id)
            if due_date(self.herd.get(cow_id)):
                self.request_notifications()
        actions.add_widget(button('Kaydet',save))

    def attach_photo(self,cow_id,path,temporary=False):
        if self.closed:
            if temporary: Path(path).unlink(missing_ok=True)
            return
        destination = None
        try:
            previous = self.herd.get(cow_id)['photo_path']
            destination = import_photo(path,Path(self.user_data_dir)/'photos')
            self.herd.set_photo(cow_id,destination)
            self.cleanup_photo(previous)
        except (ValueError,OSError,sqlite3.Error) as exc:
            if destination: Path(destination).unlink(missing_ok=True)
            self.notice(str(exc)); return
        finally:
            if temporary: Path(path).unlink(missing_ok=True)
        if self.current_id==cow_id: self.profile(cow_id)

    def reset_photo(self,cow_id):
        previous = self.herd.get(cow_id)['photo_path']
        self.herd.set_photo(cow_id,'')
        self.cleanup_photo(previous)
        self.profile(cow_id)

    def cleanup_photo(self,path):
        try:
            remove_unused_photo(path,Path(self.user_data_dir)/'photos',
                                [c['photo_path'] for c in self.herd.all()])
        except OSError:
            Logger.exception('Surum: Eski fotoğraf temizlenemedi')

    def photo_options(self,cow_id):
        popup,body,error,actions=self.dialog('Hayvanın fotoğrafı')
        def run(action):
            popup.dismiss(); action(cow_id)
        body.add_widget(button('Fotoğraf çek',lambda *_:run(self.camera)))
        body.add_widget(button('Galeriden seç',lambda *_:run(self.choose_photo)))
        if self.herd.get(cow_id)['photo_path']:
            body.add_widget(button('Temsili görseli kullan',lambda *_:run(self.reset_photo)))

    def choose_photo(self,cow_id):
        if platform=='android':
            from android_picker import AndroidPicker
            if not hasattr(self,'picker'): self.picker = AndroidPicker(Path(self.user_data_dir)/'photo-cache')
            self.picker.open(lambda path:self.attach_photo(cow_id,path,True),self.notice)
            return
        from kivy.uix.filechooser import FileChooserListView
        popup,body,error,actions = self.dialog('Fotoğraf seç')
        chooser = FileChooserListView(path=str(Path.home()),filters=['*.jpg','*.jpeg','*.png','*.JPG','*.PNG'],size_hint_y=None,height=dp(360)); body.add_widget(chooser)
        def selected(*_):
            if not chooser.selection: error.text = 'Bir fotoğraf seçin.'; return
            path = chooser.selection[0]; popup.dismiss(); self.attach_photo(cow_id,path)
        actions.add_widget(button('Kullan',selected))

    def camera(self,cow_id):
        if platform=='android':
            from android.permissions import Permission, check_permission, request_permissions
            if not check_permission(Permission.CAMERA):
                def permission_result(permissions,grants):
                    if grants and all(grants): Clock.schedule_once(lambda _:self.open_camera(cow_id))
                    else: Clock.schedule_once(lambda _:self.notice('Fotoğraf çekmek için kamera izni gerekli. Galeriden de seçebilirsin.'))
                request_permissions([Permission.CAMERA],permission_result)
                return
        self.open_camera(cow_id)

    def open_camera(self,cow_id):
        if platform == 'android':
            try:
                from android_camera import AndroidCamera
                if not hasattr(self, 'native_camera'): self.native_camera = AndroidCamera()
                self.native_camera.open(lambda path:self.attach_photo(cow_id,path), self.notice)
            except Exception:
                Logger.exception('Surum: Kamera açılamadı')
                self.notice('Kamera açılamadı. Galeriden fotoğraf seçebilirsin.')
            return
        camera = None
        try:
            from kivy.uix.camera import Camera
            camera = Camera(index=0,play=True,resolution=(1280,720))
        except Exception:
            if camera is not None: camera.play = False
            self.notice('Kamera açılamadı. İzinleri kontrol et veya fotoğraf seç.'); return
        popup,body,error,actions = self.dialog('Hayvanın fotoğrafını çek')
        self.camera_popup = popup
        camera.size_hint_y = None; camera.height = dp(360); body.add_widget(camera)
        def stop(*_):
            camera.play = False
            if platform=='android' and getattr(camera, '_camera', None) is not None:
                release = getattr(camera._camera, '_release_camera', None)
                if callable(release):
                    try:
                        release()
                    except Exception:
                        pass
            self.camera_popup = None
        popup.bind(on_dismiss=stop)
        def capture(*_):
            if camera.texture is None: error.text = 'Kamera henüz hazır değil.'; return
            from uuid import uuid4
            folder = Path(self.user_data_dir)/'photo-cache'; folder.mkdir(parents=True,exist_ok=True)
            path = folder/(uuid4().hex+'.png')
            try: camera.texture.save(str(path))
            except Exception:
                path.unlink(missing_ok=True); error.text = 'Fotoğraf kaydedilemedi.'; return
            popup.dismiss(); self.attach_photo(cow_id,str(path),True)
        actions.add_widget(button('Çek ve kullan',capture))

    def on_pause(self):
        self.sync_reminders()
        if self.camera_popup: self.camera_popup.dismiss()
        return True

    def on_start(self):
        if platform == 'android':
            try:
                from android_runtime import install
                self.android_bridge = install(self)
            except Exception:
                Logger.exception('Surum: Güvenli ekran alanı uygulanamadı')
        if reminder_plan(self.herd.all()):
            Clock.schedule_once(lambda _:self.request_notifications(),1)

    def on_resume(self):
        self.sync_reminders(force=True)
        self.tick()

    def on_stop(self):
        self.closed = True
        if self.camera_popup: self.camera_popup.dismiss()
        self.herd.close()

if __name__=='__main__': SuruApp().run()
