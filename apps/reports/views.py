from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponse
from django.utils import timezone
from django.db.models import Q
import datetime
from io import BytesIO
import html

# ReportLab imports for generating analytical PDFs
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Import existing module models
from apps.animals.models import Animal
from apps.devices.models import Device
from apps.monitoring.models import SensorReading
from apps.alerts.models import Alert
from apps.hormones.models import HormoneReservoir, HormoneRelease
from apps.protocols.models import TreatmentProtocol, TreatmentAssignment


def p(text, style):
    """Safely escape and wrap text in a ReportLab Paragraph flowable"""
    if text is None:
        text = "N/A"
    return Paragraph(html.escape(str(text)), style)


def get_report_data(report_type, start_date=None, end_date=None, animal_id=None):
    """Fetch database records for dashboard preview and PDF generation"""
    # Parse dates if passed as string
    if isinstance(start_date, str) and start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str) and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
    headers = []
    rows = []
    title = ""
    
    if report_type == 'animal_health':
        title = "Animal Health & Details Report"
        queryset = Animal.objects.all()
        if animal_id:
            queryset = queryset.filter(id=animal_id)
        if start_date:
            queryset = queryset.filter(registration_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(registration_date__lte=end_date)
            
        headers = ['Animal ID', 'Name', 'Breed', 'Age', 'Weight (kg)', 'Health Status', 'Reproductive Status', 'Assigned Devices']
        queryset = queryset.prefetch_related('devices')
        
        for animal in queryset:
            devices_str = ", ".join([d.name for d in animal.devices.all()]) or "None"
            rows.append({
                'animal_id': animal.animal_id,
                'name': animal.name,
                'breed': animal.breed,
                'age': f"{animal.age} yrs",
                'weight': f"{animal.weight}",
                'health_status': animal.get_health_status_display(),
                'reproductive_status': animal.get_reproductive_status_display(),
                'devices': devices_str
            })
            
    elif report_type == 'iot_monitoring':
        title = "IoT Sensor Readings Report"
        queryset = SensorReading.objects.all().select_related('animal', 'device')
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
            
        headers = ['Timestamp', 'Animal ID', 'Device', 'Sensor Type', 'Value', 'Unit', 'Status']
        
        # Limit preview dashboard rows to 100, but show all in PDF
        for reading in queryset[:100]:
            rows.append({
                'timestamp': reading.timestamp.strftime('%Y-%m-%d %H:%M'),
                'animal_id': reading.animal.animal_id,
                'device': reading.device.name,
                'sensor_type': reading.get_sensor_type_display(),
                'value': f"{reading.value:.2f}",
                'unit': reading.unit,
                'is_abnormal': "Abnormal" if reading.is_abnormal else "Normal"
            })
            
    elif report_type == 'alert_history':
        title = "IoT Alert Log & History Report"
        queryset = Alert.objects.all().select_related('animal', 'device')
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
            
        headers = ['Timestamp', 'Alert Title', 'Severity', 'Animal ID', 'Device', 'Status']
        
        for alert in queryset:
            rows.append({
                'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M'),
                'title': alert.title,
                'severity': alert.get_severity_display(),
                'animal_id': alert.animal.animal_id if alert.animal else "N/A",
                'device': alert.device.name if alert.device else "N/A",
                'status': alert.get_status_display()
            })
            
    elif report_type == 'treatment_hormone':
        title = "Treatment Protocol & Hormone Reservoir Report"
        assignments = TreatmentAssignment.objects.all().select_related('animal', 'protocol', 'assigned_by')
        if animal_id:
            assignments = assignments.filter(animal_id=animal_id)
        if start_date:
            assignments = assignments.filter(start_date__gte=start_date)
        if end_date:
            assignments = assignments.filter(end_date__lte=end_date)
            
        headers = ['Start Date', 'Animal ID', 'Protocol', 'Progress', 'Assigned By', 'Status']
        
        for assign in assignments:
            rows.append({
                'start_date': assign.start_date.strftime('%Y-%m-%d'),
                'animal_id': assign.animal.animal_id,
                'protocol': assign.protocol.name,
                'progress': f"{assign.progress}%",
                'assigned_by': assign.assigned_by.get_full_name() if assign.assigned_by else "System",
                'status': assign.get_status_display()
            })
            
    return {
        'title': title,
        'headers': headers,
        'rows': rows,
        'report_type': report_type
    }


class ReportsDashboardView(LoginRequiredMixin, View):
    template_name = 'reports/report_dashboard.html'

    def get(self, request):
        # Fetch summaries for counters
        total_animals = Animal.objects.count()
        active_devices = Device.objects.filter(status='active').count()
        total_alerts = Alert.objects.count()
        total_protocols = TreatmentProtocol.objects.count()

        # Query filters
        report_type = request.GET.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        animal_id = request.GET.get('animal')

        # Dropdown options
        animals_list = Animal.objects.all().order_by('animal_id')

        report_data = None
        if report_type:
            report_data = get_report_data(report_type, start_date, end_date, animal_id)

        context = {
            'total_animals': total_animals,
            'active_devices': active_devices,
            'total_alerts': total_alerts,
            'total_protocols': total_protocols,
            'animals_list': animals_list,
            'report_data': report_data,
            'selected_report_type': report_type,
            'selected_start_date': start_date,
            'selected_end_date': end_date,
            'selected_animal': animal_id
        }
        return render(request, self.template_name, context)


class GenerateReportPDFView(LoginRequiredMixin, View):
    def get(self, request):
        report_type = request.GET.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        animal_id = request.GET.get('animal')

        if not report_type:
            raise Http404("Report type not specified")

        # Fetch animal details if selected
        animal_obj = None
        if animal_id:
            try:
                animal_obj = Animal.objects.get(id=animal_id)
            except Animal.DoesNotExist:
                pass

        # Setup pdf details
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Colors conforming to dark blue palette
        primary_color = colors.HexColor("#0f172a")
        accent_color = colors.HexColor("#1e40af")
        text_color = colors.HexColor("#334155")
        border_color = colors.HexColor("#cbd5e1")
        light_bg = colors.HexColor("#f8fafc")

        # Typography style configurations
        title_style = ParagraphStyle(
            'PDFTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=primary_color,
            spaceAfter=4
        )
        
        subtitle_style = ParagraphStyle(
            'PDFSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=accent_color,
            spaceAfter=15
        )

        meta_label_style = ParagraphStyle(
            'PDFMetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=primary_color
        )

        meta_val_style = ParagraphStyle(
            'PDFMetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=text_color
        )

        th_style = ParagraphStyle(
            'PDFTH',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            textColor=colors.white
        )

        td_style = ParagraphStyle(
            'PDFTD',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=text_color
        )

        section_heading_style = ParagraphStyle(
            'PDFSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=primary_color,
            spaceBefore=15,
            spaceAfter=8
        )

        story = []

        # Header Block
        story.append(Paragraph("YAKSYNC SMART MONITORING SYSTEM", title_style))
        story.append(Paragraph("LIVESTOCK ANALYTICAL REPORT", subtitle_style))

        # Metadata Layout
        meta_data = [
            [
                Paragraph("Report Type:", meta_label_style),
                Paragraph(report_type.replace('_', ' ').title(), meta_val_style),
                Paragraph("Generated On:", meta_label_style),
                Paragraph(timezone.now().strftime('%Y-%m-%d %H:%M %Z'), meta_val_style),
            ],
            [
                Paragraph("Generated By:", meta_label_style),
                Paragraph(request.user.get_full_name() or request.user.username, meta_val_style),
                Paragraph("Date Range:", meta_label_style),
                Paragraph(f"{start_date or 'Beginning'} to {end_date or 'Present'}", meta_val_style),
            ],
            [
                Paragraph("Selected Animal:", meta_label_style),
                Paragraph(f"{animal_obj.animal_id} ({animal_obj.name})" if animal_obj else "All Animals", meta_val_style),
                Paragraph("", meta_label_style),
                Paragraph("", meta_val_style),
            ]
        ]
        
        meta_table = Table(meta_data, colWidths=[100, 160, 100, 160])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # Reports Contents
        if report_type == 'animal_health':
            # Run query
            queryset = Animal.objects.all()
            if animal_id:
                queryset = queryset.filter(id=animal_id)
            if start_date:
                queryset = queryset.filter(registration_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(registration_date__lte=end_date)
            queryset = queryset.prefetch_related('devices')

            # Build table columns
            headers = ['Animal ID', 'Name', 'Breed', 'Age', 'Weight', 'Health', 'Reproduction', 'Devices']
            col_widths = [60, 60, 65, 45, 55, 65, 75, 95]
            
            table_data = [[p(h, th_style) for h in headers]]
            
            for index, animal in enumerate(queryset):
                devices_str = ", ".join([d.name for d in animal.devices.all()]) or "None"
                table_data.append([
                    p(animal.animal_id, td_style),
                    p(animal.name, td_style),
                    p(animal.breed, td_style),
                    p(f"{animal.age} yrs", td_style),
                    p(f"{animal.weight} kg", td_style),
                    p(animal.get_health_status_display(), td_style),
                    p(animal.get_reproductive_status_display(), td_style),
                    p(devices_str, td_style)
                ])

            main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]
            
            # Alternating rows
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
                    
            main_table.setStyle(TableStyle(t_style))
            story.append(main_table)

        elif report_type == 'iot_monitoring':
            queryset = SensorReading.objects.all().select_related('animal', 'device')
            if animal_id:
                queryset = queryset.filter(animal_id=animal_id)
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)

            headers = ['Timestamp', 'Animal ID', 'Device', 'Sensor Type', 'Value', 'Unit', 'Status']
            col_widths = [100, 65, 80, 100, 50, 50, 75]
            
            table_data = [[p(h, th_style) for h in headers]]
            
            for index, reading in enumerate(queryset):
                status_str = "Abnormal" if reading.is_abnormal else "Normal"
                table_data.append([
                    p(reading.timestamp.strftime('%Y-%m-%d %H:%M'), td_style),
                    p(reading.animal.animal_id, td_style),
                    p(reading.device.name, td_style),
                    p(reading.get_sensor_type_display(), td_style),
                    p(f"{reading.value:.2f}", td_style),
                    p(reading.unit, td_style),
                    p(status_str, td_style)
                ])

            main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]
            
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
                    
            main_table.setStyle(TableStyle(t_style))
            story.append(main_table)

        elif report_type == 'alert_history':
            queryset = Alert.objects.all().select_related('animal', 'device')
            if animal_id:
                queryset = queryset.filter(animal_id=animal_id)
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)

            headers = ['Timestamp', 'Alert Title', 'Severity', 'Animal ID', 'Device', 'Status']
            col_widths = [100, 150, 60, 60, 80, 70]
            
            table_data = [[p(h, th_style) for h in headers]]
            
            for index, alert in enumerate(queryset):
                table_data.append([
                    p(alert.timestamp.strftime('%Y-%m-%d %H:%M'), td_style),
                    p(alert.title, td_style),
                    p(alert.get_severity_display(), td_style),
                    p(alert.animal.animal_id if alert.animal else "N/A", td_style),
                    p(alert.device.name if alert.device else "N/A", td_style),
                    p(alert.get_status_display(), td_style)
                ])

            main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]
            
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
                    
            main_table.setStyle(TableStyle(t_style))
            story.append(main_table)

        elif report_type == 'treatment_hormone':
            # Section 1: Reservoirs (all)
            story.append(Paragraph("1. Hormone Reservoirs Status", section_heading_style))
            reservoirs = HormoneReservoir.objects.all()
            res_headers = ['Hormone Type', 'Initial Qty', 'Current Qty', 'Unit', 'Alert Status']
            res_widths = [150, 90, 90, 90, 100]
            res_data = [[p(h, th_style) for h in res_headers]]
            
            for res in reservoirs:
                res_data.append([
                    p(res.hormone_type, td_style),
                    p(f"{res.initial_quantity:.2f}", td_style),
                    p(f"{res.current_quantity:.2f}", td_style),
                    p(res.unit, td_style),
                    p("LOW" if res.is_low else "Sufficient", td_style)
                ])
                
            res_table = Table(res_data, colWidths=res_widths)
            res_t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), accent_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
            for i in range(1, len(res_data)):
                if i % 2 == 0:
                    res_t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
            res_table.setStyle(TableStyle(res_t_style))
            story.append(res_table)
            story.append(Spacer(1, 15))

            # Section 2: Treatment Assignments
            story.append(Paragraph("2. Treatment Protocol Assignments", section_heading_style))
            assignments = TreatmentAssignment.objects.all().select_related('animal', 'protocol', 'assigned_by')
            if animal_id:
                assignments = assignments.filter(animal_id=animal_id)
            if start_date:
                assignments = assignments.filter(start_date__gte=start_date)
            if end_date:
                assignments = assignments.filter(end_date__lte=end_date)

            assign_headers = ['Start Date', 'Animal ID', 'Protocol', 'Progress', 'Assigned By', 'Status']
            assign_widths = [80, 70, 150, 60, 80, 80]
            assign_data = [[p(h, th_style) for h in assign_headers]]
            
            for assign in assignments:
                assign_data.append([
                    p(assign.start_date.strftime('%Y-%m-%d'), td_style),
                    p(assign.animal.animal_id, td_style),
                    p(assign.protocol.name, td_style),
                    p(f"{assign.progress}%", td_style),
                    p(assign.assigned_by.get_full_name() if assign.assigned_by else "System", td_style),
                    p(assign.get_status_display(), td_style)
                ])
                
            assign_table = Table(assign_data, colWidths=assign_widths)
            assign_t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
            for i in range(1, len(assign_data)):
                if i % 2 == 0:
                    assign_t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
            assign_table.setStyle(TableStyle(assign_t_style))
            story.append(assign_table)
            story.append(Spacer(1, 15))

            # Section 3: Hormone Releases
            story.append(Paragraph("3. Hormone Releases History", section_heading_style))
            releases = HormoneRelease.objects.all().select_related('animal', 'reservoir', 'performed_by')
            if animal_id:
                releases = releases.filter(animal_id=animal_id)
            if start_date:
                releases = releases.filter(timestamp__date__gte=start_date)
            if end_date:
                releases = releases.filter(timestamp__date__lte=end_date)

            rel_headers = ['Timestamp', 'Animal ID', 'Hormone Type', 'Quantity', 'Performed By']
            rel_widths = [120, 80, 140, 80, 100]
            rel_data = [[p(h, th_style) for h in rel_headers]]
            
            for rel in releases:
                rel_data.append([
                    p(rel.timestamp.strftime('%Y-%m-%d %H:%M'), td_style),
                    p(rel.animal.animal_id, td_style),
                    p(rel.reservoir.hormone_type, td_style),
                    p(f"{rel.quantity:.2f} {rel.reservoir.unit}", td_style),
                    p(rel.performed_by.get_full_name() if rel.performed_by else "System", td_style)
                ])
                
            rel_table = Table(rel_data, colWidths=rel_widths)
            rel_t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), accent_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
            for i in range(1, len(rel_data)):
                if i % 2 == 0:
                    rel_t_style.append(('BACKGROUND', (0, i), (-1, i), light_bg))
            rel_table.setStyle(TableStyle(rel_t_style))
            story.append(rel_table)

        # Build document
        doc.build(story)

        # Get file contents and send response
        buffer.seek(0)
        
        # Name matching requested format: YakSync_<Type>_Report_YYYYMMDD.pdf
        date_str = datetime.date.today().strftime('%Y%m%d')
        type_clean = report_type.replace('_', ' ').title().replace(' ', '_')
        filename = f"YakSync_{type_clean}_Report_{date_str}.pdf"

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
