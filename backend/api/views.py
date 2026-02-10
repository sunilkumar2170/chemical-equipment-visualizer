from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import DatasetUpload
from .serializers import DatasetUploadSerializer
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os
import traceback


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chemical equipment datasets
    """
    queryset = DatasetUpload.objects.all()
    serializer_class = DatasetUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets for current user - NO SLICE to allow get_object()"""
        return DatasetUpload.objects.filter(user=self.request.user).order_by('-upload_date')
    
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """
        Upload and process CSV file containing equipment data
        """
        try:
            # Get uploaded file
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file extension
            if not csv_file.name.endswith('.csv'):
                return Response(
                    {'error': 'Please upload a CSV file'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read CSV file
            try:
                df = pd.read_csv(csv_file)
            except pd.errors.EmptyDataError:
                return Response(
                    {'error': 'CSV file is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Error reading CSV: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate required columns
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return Response({
                    'error': f'Missing required columns: {", ".join(missing_cols)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate statistics
            total_count = len(df)
            
            
            try:
                avg_flowrate = float(df['Flowrate'].astype(float).mean())
                avg_pressure = float(df['Pressure'].astype(float).mean())
                avg_temperature = float(df['Temperature'].astype(float).mean())
            except Exception as e:
                return Response(
                    {'error': f'Invalid numeric data in CSV: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get equipment distribution
            equipment_dist = df['Type'].value_counts().to_dict()
            
            # Reset file pointer for saving
            csv_file.seek(0)
            
            # Create dataset record
            dataset = DatasetUpload.objects.create(
                user=request.user,
                filename=csv_file.name,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature,
                equipment_distribution=equipment_dist,
                csv_file=csv_file
            )
            
            # Keep only last 5 datasets per user
            user_datasets = DatasetUpload.objects.filter(
                user=request.user
            ).order_by('-upload_date')
            
            if user_datasets.count() > 5:
                old_datasets = list(user_datasets[5:])
                for old in old_datasets:
                    # Delete associated file
                    if old.csv_file:
                        try:
                            if os.path.exists(old.csv_file.path):
                                os.remove(old.csv_file.path)
                        except Exception:
                            pass
                    old.delete()
            
            # Serialize response
            serializer = self.get_serializer(dataset)
            
            # Return response with data
            return Response({
                'message': 'File uploaded successfully',
                'data': serializer.data,
                'statistics': {
                    'total_count': total_count,
                    'avg_flowrate': avg_flowrate,
                    'avg_pressure': avg_pressure,
                    'avg_temperature': avg_temperature,
                    'equipment_distribution': equipment_dist
                },
                'rows': df.to_dict('records')
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Log the error
            print("Upload Error:", traceback.format_exc())
            return Response(
                {'error': f'Error processing file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """
        Generate PDF report for a dataset
        """
        try:
            # Get dataset
            dataset = self.get_object()
            
            # Check if CSV file exists
            if not dataset.csv_file:
                return Response(
                    {'error': 'No CSV file associated with this dataset'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not os.path.exists(dataset.csv_file.path):
                return Response(
                    {'error': 'CSV file not found on server'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Read CSV file
            df = pd.read_csv(dataset.csv_file.path)
            
            # Create PDF in memory
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=50,
                bottomMargin=40
            )
            
            # Container for PDF elements
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=26,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#764ba2'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            # Title
            title = Paragraph("Chemical Equipment Data Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.3*inch))
            
            # Report information
            info_data = [
                ['Report Generated:', dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S')],
                ['Dataset Filename:', dataset.filename],
                ['Total Equipment:', str(dataset.total_count)],
                ['Generated By:', request.user.username],
            ]
            
            info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.4*inch))
            
            # Summary Statistics Section
            elements.append(Paragraph("Summary Statistics", heading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            stats_data = [
                ['Parameter', 'Average Value', 'Unit'],
                ['Flowrate', f'{dataset.avg_flowrate:.2f}', 'L/min'],
                ['Pressure', f'{dataset.avg_pressure:.2f}', 'bar'],
                ['Temperature', f'{dataset.avg_temperature:.2f}', '°C'],
            ]
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Equipment Distribution Section
            elements.append(Paragraph("Equipment Type Distribution", heading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            dist_data = [['Equipment Type', 'Count', 'Percentage']]
            for equip_type, count in sorted(dataset.equipment_distribution.items()):
                percentage = (count / dataset.total_count) * 100
                dist_data.append([
                    str(equip_type), 
                    str(count),
                    f'{percentage:.1f}%'
                ])
            
            dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            dist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(dist_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Equipment Details Section
            elements.append(Paragraph("Equipment Details", heading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Table headers
            detail_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
            
            # Add data rows (limit to prevent overflow)
            max_rows = min(25, len(df))
            for idx, row in df.head(max_rows).iterrows():
                detail_data.append([
                    str(row['Equipment Name'])[:20],
                    str(row['Type'])[:15],
                    f"{float(row['Flowrate']):.1f}",
                    f"{float(row['Pressure']):.1f}",
                    f"{float(row['Temperature']):.1f}"
                ])
            
            detail_table = Table(
                detail_data, 
                colWidths=[2*inch, 1.4*inch, 1*inch, 1*inch, 1*inch]
            )
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(detail_table)
            
            # Add note if data was truncated
            if len(df) > max_rows:
                elements.append(Spacer(1, 0.15*inch))
                note_style = ParagraphStyle(
                    'Note',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Oblique'
                )
                note = Paragraph(
                    f"Showing first {max_rows} of {len(df)} total equipment records",
                    note_style
                )
                elements.append(note)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Create HTTP response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
            
            return response
            
        except FileNotFoundError as e:
            print("File Not Found Error:", str(e))
            return Response(
                {'error': 'CSV file not found on server'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log detailed error
            print("PDF Generation Error:", traceback.format_exc())
            return Response(
                {'error': f'PDF generation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get upload history for current user (last 5 datasets)
        """
        try:
            # Apply [:5] limit ONLY in this endpoint
            datasets = DatasetUpload.objects.filter(
                user=request.user
            ).order_by('-upload_date')[:5]
            
            # Convert to list to get count
            datasets_list = list(datasets)
            serializer = self.get_serializer(datasets_list, many=True)
            
            return Response({
                'count': len(datasets_list),
                'datasets': serializer.data
            })
        except Exception as e:
            print("History Error:", traceback.format_exc())
            return Response(
                {'error': f'Error fetching history: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )