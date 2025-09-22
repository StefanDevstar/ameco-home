from flask import *
from database import *
from helpers import save_to_excel, FetchLogs

Export = Blueprint('Exporter', __name__, url_prefix='/export')

# [Partial, Buyer, Seller (Pending, All)] ✅
# Properties ✅
# Url Report
# API
# Database 

# /export/all/properties ✅
# /export/{{type}}/id/{{lead.NewLeadId}} ✅
# /export/{{type}}/{{Sort}} ->(Pending, All) ✅

@Export.before_request
def before_request():
    if not session.get('is_loggedin') and not session.get('username'):
        return redirect(url_for('auth.login'))
    else:
        g.username = session.get('username')

@Export.route('/all/properties')
def all_properties():
    Data = PropertyData.fetch_all()
    filepath = save_to_excel("PropertyData-Export-All.xlsx", Data)
    return send_file(filepath, as_attachment=True)

@Export.route('/<type>/id/<id>')
def export_by_id(type, id):
    Data = []
    if type == "Partial":
        Data = [PartialLeads.ListById(id)]
    else:
        Data = [Leads.ListById(id)]

    filepath = save_to_excel(f"LeadData-Export-{id}.xlsx", Data)
    return send_file(filepath, as_attachment=True)

@Export.route('/<type>/<sort>')
def export_by_sort(type, sort):
    if type == "buyer":
        Data = Leads.ListAll()
        data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
        if sort == "Pending":
            data = [lead for lead in data if not lead['Admin_resp']]
        elif sort == "All":
            data = [lead for lead in data if lead['Are you looking to buy']]
    elif type == "seller":
        Data = Leads.ListAll()
        data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
        if sort == "Pending":
            data = [lead for lead in data if not lead['Admin_resp']]
        elif sort == "All":
            data = [lead for lead in data if not lead['Are you looking to buy']]
    elif type == "Partial":
        Data = PartialLeads.ListAll()
        data = [{**lead, 'Datetime': lead['Datetime'].strftime('%d/%m/%Y')}  for lead in Data ]
        if sort == "Pending":
            data = [lead for lead in data if not lead['Admin_Resp']]
        elif sort == "All":
            data = [lead for lead in data if lead['Admin_Resp']]

    filepath = save_to_excel(f"LeadData-Export-{type}-{sort}.xlsx", data)
    return send_file(filepath, as_attachment=True)
    
@Export.route('/all/Api/export')
def all_api_export():
    Data = FetchLogs()
    data = [{ 'SID': log.sid, 'Date Sent': log.date_sent.strftime('%d/%m/%Y') if log.date_sent else None, 'From': log.from_, 'To': log.to, 'Body': log.body, 'Status': log.status} for log in Data]
    filepath = save_to_excel("API-Logs-Export-All.xlsx", data)
    return send_file(filepath, as_attachment=True)

@Export.route('/all/url/export')
def all_url_export():
    Data = URLTrack.ListAll()
    data = [{**url, 'Datetime': url['CreatedOn'].strftime('%d/%m/%Y')}  for url in Data ]
    filepath = save_to_excel("URL-Track-Export-All.xlsx", data)
    return send_file(filepath, as_attachment=True)
    