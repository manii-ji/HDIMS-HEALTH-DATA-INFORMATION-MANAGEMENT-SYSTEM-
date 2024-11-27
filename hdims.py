from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.progressbar import MDProgressBar
from data_manager import DataManager
from collections import Counter
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

import os

# Initialize DataManager as a singleton
data_manager_instance = DataManager()

class ChartCard(MDCard):
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(600)  # Increased height
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 4
        
        # Add title
        self.add_widget(MDLabel(
            text=title,
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))
        
        # Container for bars/data
        self.data_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=[0, dp(20), 0, 0],
            size_hint_y=None
        )
        self.data_container.bind(minimum_height=self.data_container.setter('height'))
        
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        scroll.add_widget(self.data_container)
        self.add_widget(scroll)

class DataBar(MDBoxLayout):
    def __init__(self, label, value, max_value, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = dp(4)
        
        # Label and value
        label_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(30)
        )
        label_box.add_widget(MDLabel(
            text=label,
            size_hint_x=0.7,
            halign='left'
        ))
        label_box.add_widget(MDLabel(
            text=str(value),
            size_hint_x=0.3,
            halign='right'
        ))
        self.add_widget(label_box)
        
        # Progress bar
        progress = MDProgressBar(
            value=(value / max_value * 100) if max_value > 0 else 0,
            size_hint_y=None,
            height=dp(20)
        )
        self.add_widget(progress)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=20, 
            padding=40
        )
          
        card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(300, 400),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=6,
            padding=20
        )  
       
        card.add_widget(MDLabel(text="Welcome to HDIMS", halign="center", font_style="H5"))
        self.username_input = MDTextField(hint_text="Enter Username", icon_right="account")
        self.password_input = MDTextField(hint_text="Enter Password", password=True, icon_right="eye-off")
        login_button = MDRaisedButton(text="Login", on_release=self.validate_credentials, size_hint_x=1)
        
        card.add_widget(self.username_input)
        card.add_widget(self.password_input)
        card.add_widget(login_button)
        
        layout.add_widget(card)
        self.add_widget(layout)
    
    def validate_credentials(self, instance):
        if self.username_input.text == "hdims" and self.password_input.text == "admin":
            self.manager.current = 'home'
        else:
            print("Invalid credentials")

class HomeScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="HDIMS Home",
            left_action_items=[["help", lambda x: self.show_help()]],
            right_action_items=[
                ["refresh", lambda x: self.refresh_data()],
                
            ]
        )
        layout.add_widget(toolbar)
        
        self.content = MDBoxLayout(orientation='vertical', spacing=20, padding=40)
        
        self.stats_grid = MDGridLayout(cols=2, spacing=20, size_hint_y=None, height=200)
        
        self.hospital_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=180,
            padding=15,
            elevation=4
        )
        self.hospital_card.add_widget(MDLabel(
            text="[size=36][font=Icons]hospital-building[/font][/size]",
            markup=True,
            halign="center"
        ))
        self.hospital_count_label = MDLabel(
            text=str(self.data_manager.get_unique_hospitals_count()),
            halign="center",
            font_style="H4"
        )
        self.hospital_card.add_widget(self.hospital_count_label)
        self.hospital_card.add_widget(MDLabel(
            text="Connected Hospitals",
            halign="center"
        ))
        
        self.patient_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=180,
            padding=15,
            elevation=4
        )
        self.patient_card.add_widget(MDLabel(
            text="[size=36][font=Icons]account-group[/font][/size]",
            markup=True,
            halign="center"
        ))
        self.patient_count_label = MDLabel(
            text=str(self.data_manager.get_total_patients_count()),
            halign="center",
            font_style="H4"
        )
        self.patient_card.add_widget(self.patient_count_label)
        self.patient_card.add_widget(MDLabel(
            text="Total Patients",
            halign="center"
        ))
        
        self.stats_grid.add_widget(self.hospital_card)
        self.stats_grid.add_widget(self.patient_card)
        self.content.add_widget(self.stats_grid)
        
        buttons_box = MDBoxLayout(orientation='vertical', spacing=20, padding=(0, 20, 0, 0))
        buttons_box.add_widget(
            MDRaisedButton(                     
                text="Enter/Update Hospital Data",
                on_release=self.open_hospital_data,
                size_hint_x=0.8,
                pos_hint={'center_x': 0.5}
            )
        )
        buttons_box.add_widget(
            MDRaisedButton(
                text="View Data",
                on_release=self.open_view_data,
                size_hint_x=0.8,
                pos_hint={'center_x': 0.5}
            )
        )
        buttons_box.add_widget(
            MDRaisedButton(
                text="Analyze Data",
                on_release=self.open_analysis,
                size_hint_x=0.8,
                pos_hint={'center_x': 0.5},
            )
        )
        self.content.add_widget(buttons_box)
        
        layout.add_widget(self.content)
        self.add_widget(layout)
    
    def open_hospital_data(self, instance):
        self.manager.current = 'hospital_data'
    
    def open_view_data(self, instance):
        self.manager.current = 'view_data'
    
    def open_analysis(self, instance):
        self.manager.current = 'analysis'
    
    def refresh_data(self):
        self.hospital_count_label.text = str(self.data_manager.get_unique_hospitals_count())
        self.patient_count_label.text = str(self.data_manager.get_total_patients_count())
    
    def show_help(self):
        help_dialog = MDDialog(
            title="HDIMS Home Help",
            text=(
                "Welcome to Hospital Data Information Management System!\n\n"
                "• View hospital and patient statistics at a glance\n"
                "• Enter/Update Hospital Data: Add new patient records\n"
                "• View Data: See all patient records in a table format\n"
                "• Analyze Data: View detailed charts and statistics\n"
                "• Use the refresh button to update the statistics\n"
                "\nClick on any button to navigate to the respective section."
            ),
            buttons=[
                MDFlatButton(
                    text="GOT IT",
                    on_release=lambda x: help_dialog.dismiss()
                )
            ]
        )
        help_dialog.open()
class HospitalDataScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(HospitalDataScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Hospital Data Entry",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["file-excel", lambda x: self.open_excel_file()]]
        )
        layout.add_widget(toolbar)
        
        content = MDBoxLayout(orientation='vertical', spacing=20, padding=40)
        
        self.hospital_name = MDTextField(hint_text="Enter Hospital Name", icon_right="hospital-building")
        self.patient_name = MDTextField(hint_text="Enter Patient Name", icon_right="account")
        self.disease_name = MDTextField(hint_text="Enter Disease Name", icon_right="virus")
        self.doctor_name = MDTextField(hint_text="Enter Doctor Name", icon_right="doctor")
        submit_button = MDRaisedButton(text="Submit Data", on_release=self.submit_data, size_hint_x=0.8, pos_hint={'center_x': 0.5})
        
        content.add_widget(self.hospital_name)
        content.add_widget(self.patient_name)
        content.add_widget(self.disease_name)
        content.add_widget(self.doctor_name)
        content.add_widget(submit_button)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def submit_data(self, instance):
        self.data_manager.add_data(
            self.hospital_name.text,
            self.patient_name.text,
            self.disease_name.text,
            self.doctor_name.text
        )
        self.clear_fields()
    
    def clear_fields(self):
        self.hospital_name.text = ""
        self.patient_name.text = ""
        self.disease_name.text = ""
        self.doctor_name.text = ""
    
    def go_back(self):
        self.manager.current = 'home'
    
    def open_excel_file(self):
        if os.path.exists(DataManager.EXCEL_FILE):
            os.system(f'start {DataManager.EXCEL_FILE}')

class ViewDataScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(ViewDataScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="View Data",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
               
                ["file-excel", lambda x: self.open_excel_file()],
                ["refresh", lambda x: self.refresh_data()]
            ]
        )
        layout.add_widget(toolbar)
        
        content = MDBoxLayout(orientation='vertical', spacing=20, padding=20)
        
        self.data_table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("Hospital Name", dp(30)),
                ("Patient Name", dp(30)),
                ("Disease Name", dp(30)),
                ("Doctor Name", dp(30))
            ],
            row_data=self.data_manager.get_all_data()
        )
        
        content.add_widget(self.data_table)
        layout.add_widget(content)
        
        self.add_widget(layout)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def refresh_data(self):
        self.data_table.row_data = self.data_manager.get_all_data()
    
    def open_excel_file(self):
        if os.path.exists(DataManager.EXCEL_FILE):
            os.system(f'start {DataManager.EXCEL_FILE}')
    


class DataAnalysisScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(DataAnalysisScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Data Analysis Dashboard",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["help", lambda x: self.show_help()],
                ["refresh", lambda x: self.refresh_data()],
                                
                                ]
        )
        layout.add_widget(toolbar)
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(40)
        )
        
        # Summary card
        summary_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(16),
            spacing=dp(8),
            elevation=4
        )
        
        summary_card.add_widget(MDLabel(
            text="Data Analysis Summary",
            halign="center",
            font_style="H6"
        ))
        
        self.summary_stats = MDLabel(
            text="Loading statistics...",
            halign="center"
        )
        summary_card.add_widget(self.summary_stats)
        content.add_widget(summary_card)
        
        # Navigation buttons
        buttons = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20)
        )
        
        buttons.add_widget(MDRaisedButton(
            text="Hospital Distribution Chart",
            on_release=self.go_to_hospital_chart,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        ))
        
        buttons.add_widget(MDRaisedButton(
            text="Disease Distribution Chart",
            on_release=self.go_to_disease_chart,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        ))
        
        content.add_widget(buttons)
        layout.add_widget(content)
        self.add_widget(layout)
        self.update_summary_stats()
    
    def update_summary_stats(self):
        data = self.data_manager.get_all_data()
        total_patients = len(data)
        unique_hospitals = len(set(row[0] for row in data))
        unique_diseases = len(set(row[2] for row in data))
        
        self.summary_stats.text = (
            f"Total Patients: {total_patients}\n"
            f"Unique Hospitals: {unique_hospitals}\n"
            f"Different Diseases: {unique_diseases}"
        )
    
    def show_help(self):
        help_dialog = MDDialog(
            title="Analysis Dashboard Help",
            text=(
                "• Choose which distribution chart to view:\n"
                "• Hospital Distribution: Shows patient count per hospital\n"
                "• Disease Distribution: Shows case count per disease\n"
                "• Use refresh button in each view to update data"
            ),
            buttons=[
                MDFlatButton(
                    text="GOT IT",
                    on_release=lambda x: help_dialog.dismiss()
                )
            ]
        )
        help_dialog.open()
    
    def go_back(self):
        self.manager.current = 'home'
    
    def go_to_hospital_chart(self, instance):
        self.manager.current = 'hospital_chart'
    
    def go_to_disease_chart(self, instance):
        self.manager.current = 'disease_chart'
    
    
    
    

class HospitalChartScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(HospitalChartScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Hospital Distribution Analysis",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["refresh", lambda x: self.refresh_chart()],
                ["help", lambda x: self.show_help()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Main content
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Hospital chart
        self.hospital_chart = ChartCard(
            title="Patient Distribution by Hospital",
            md_bg_color=(0.9, 0.9, 0.9, 0.1)
        )
        content.add_widget(self.hospital_chart)
        
        # Navigation buttons
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(48),
            padding=[dp(20), 0]
        )
        
        buttons.add_widget(MDRaisedButton(
            text="View Disease Chart",
            on_release=self.go_to_disease_chart
        ))
        
        content.add_widget(buttons)
        layout.add_widget(content)
        self.add_widget(layout)
        self.refresh_chart()
    
    def refresh_chart(self):
        self.hospital_chart.data_container.clear_widgets()
        
        data = self.data_manager.get_all_data()
        hospitals = [row[0] for row in data]
        hospital_counts = Counter(hospitals)
        
        if hospital_counts:
            max_patients = max(hospital_counts.values())
            sorted_hospitals = dict(sorted(hospital_counts.items(), key=lambda x: x[1], reverse=True))
            
            for hospital, count in sorted_hospitals.items():
                self.hospital_chart.data_container.add_widget(
                    DataBar(hospital, count, max_patients)
                )
    
    def show_help(self):
        help_dialog = MDDialog(
            title="Hospital Chart Help",
            text=(
                "• Chart shows distribution of patients across hospitals\n"
                "• Bars are sorted by number of patients\n"
                "• Use refresh button to update data\n"
                "• Click hospital names for details"
            ),
            buttons=[
                MDFlatButton(
                    text="GOT IT",
                    on_release=lambda x: help_dialog.dismiss()
                )
            ]
        )
        help_dialog.open()
    
    def go_back(self):
        self.manager.current = 'analysis'
    
    def go_to_disease_chart(self, instance):
        self.manager.current = 'disease_chart'

class DiseaseChartScreen(Screen):
    data_manager = data_manager_instance
    
    def __init__(self, **kwargs):
        super(DiseaseChartScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Disease Distribution Analysis",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["refresh", lambda x: self.refresh_chart()],
                ["help", lambda x: self.show_help()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Main content
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Disease chart
        self.disease_chart = ChartCard(
            title="Disease Distribution Analysis",
            md_bg_color=(0.9, 0.9, 0.9, 0.1)
        )
        content.add_widget(self.disease_chart)
        
        # Navigation buttons
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(48),
            padding=[dp(20), 0]
        )
        
        buttons.add_widget(MDRaisedButton(
            text="View Hospital Chart",
            on_release=self.go_to_hospital_chart
        ))
        
        content.add_widget(buttons)
        layout.add_widget(content)
        self.add_widget(layout)
        self.refresh_chart()
    
    def refresh_chart(self):
        self.disease_chart.data_container.clear_widgets()
        
        data = self.data_manager.get_all_data()
        diseases = [row[2] for row in data]
        disease_counts = Counter(diseases)
        
        if disease_counts:
            max_cases = max(disease_counts.values())
            sorted_diseases = dict(sorted(disease_counts.items(), key=lambda x: x[1], reverse=True))
            
            for disease, count in sorted_diseases.items():
                self.disease_chart.data_container.add_widget(
                    DataBar(disease, count, max_cases)
                )
    
    def show_help(self):
        help_dialog = MDDialog(
            title="Disease Chart Help",
            text=(
                "• Chart shows distribution of diseases\n"
                "• Bars are sorted by number of cases\n"
                "• Use refresh button to update data\n"
                "• Click disease names for details"
            ),
            buttons=[
                MDFlatButton(
                    text="GOT IT",
                    on_release=lambda x: help_dialog.dismiss()
                )
            ]
        )
        help_dialog.open()
    
    def go_back(self):
        self.manager.current = 'analysis'
    
    def go_to_hospital_chart(self, instance):
        self.manager.current = 'hospital_chart'

class HDIMSApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Cyan'
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(HospitalDataScreen(name='hospital_data'))
        sm.add_widget(ViewDataScreen(name='view_data'))
        sm.add_widget(DataAnalysisScreen(name='analysis'))
        sm.add_widget(HospitalChartScreen(name='hospital_chart'))
        sm.add_widget(DiseaseChartScreen(name='disease_chart'))
        return sm

if __name__ == '__main__':
    HDIMSApp().run()