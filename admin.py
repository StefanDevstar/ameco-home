from flask import *
from werkzeug.utils import secure_filename
from database import Admin, PartialLeads, Leads, PropertyData, URLTrack
import os
from datetime import datetime
from helpers import FetchLogs, SendMessage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def before_request():
    g.current_path = request.path
    if not session.get('is_loggedin') and not session.get('username'):
        return redirect(url_for('auth.login'))
    else:
        g.username = session.get('username')
    

@admin_bp.route('/')
def admin_home():
    return redirect(url_for('admin.admin_hom'))

@admin_bp.route('/dashboard')
def admin_hom():
    total_leads = Leads.ListAll()
    pending_leads = [lead for lead in total_leads if not lead['Admin_resp']]
    total_url_visits = URLTrack.ListAll()
    pending_url_visits = [lead for lead in total_url_visits if not lead['FirstVistOn']]
    try:
        total_leads_count = len(total_leads)
        pending_leads_count = len(pending_leads)
        total_url_visits_count = (len(total_url_visits) - len(pending_url_visits))
        pending_url_visits_count = len(pending_url_visits)
    except:
        total_leads_count = 0
        pending_leads_count = 0
        total_url_visits_count = 0
        pending_url_visits_count = 0
 
    progress_percentage = pending_leads_count / total_leads_count * 100 if total_leads_count > 0 else 0 

    return render_template('admin/dashboard.html', progress_percentage=progress_percentage, total_logs=pending_leads_count, total_leads=total_leads_count, total_url_visits_count=total_url_visits_count, pending_url_visits_count=pending_url_visits_count)


@admin_bp.route('/pending/partial_leads')
def pending_partial_leads():
    Data = PartialLeads.ListAll()
    data = [{**lead, 'Datetime': lead['Datetime'].strftime('%d/%m/%Y')}  for lead in Data ]
    try:
        data = [lead for lead in data if not lead['Admin_Resp']]
    except:
        pass
    return render_template('admin/leads-list.html', leads=data, type="Partial", LeadType="New Parital Leads", sort="Pending")

@admin_bp.route('/all/partial_leads')
def partial_leads():
    Data = PartialLeads.ListAll()
    data = [{**lead, 'Datetime': lead['Datetime'].strftime('%d/%m/%Y')}  for lead in Data ]
    return render_template('admin/leads-list.html', leads=data, type="Partial", LeadType="All Parital Leads", sort="All")

# /admin/pending/buyer_leads ✅
# /admin/pending/seller_leads ✅
# /admin/all/buyer_leads ✅
# /admin/all/seller_leads ✅

@admin_bp.route('/pending/buyer_leads')
def pending_buyer_leads():
    Data = Leads.ListAll()

    data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
    try:
        data = [lead for lead in data if not lead['Admin_resp']]
    except:
        pass

    try:
        data = [lead for lead in data if lead['Are you looking to buy']]
    except:
        pass
    return render_template('admin/leads-list.html', leads=data, type="buyer", LeadType="New Buyer Leads", sort="Pending")

@admin_bp.route('/all/buyer_leads')
def buyer_leads():
    Data = Leads.ListAll()
    data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
    try:
        data = [lead for lead in data if lead['Are you looking to buy']]
    except:
        pass
    return render_template('admin/leads-list.html', leads=data, type="buyer", LeadType="All Buyer Leads", sort="All")

@admin_bp.route('/pending/seller_leads')
def pending_seller_leads():
    Data = Leads.ListAll()
    data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
    try:
        data = [lead for lead in data if not lead['Admin_resp']]
    except:
        pass

    try:
        data = [lead for lead in data if not lead['Are you looking to buy']]
    except:
        pass
    
    return render_template('admin/leads-list.html', leads=data, type="seller", LeadType="New Seller Leads", sort="Pending")

@admin_bp.route('/all/seller_leads')
def seller_leads():
    Data = Leads.ListAll()
    data = [{**lead, 'Datetime': lead['DateEntry'].strftime('%d/%m/%Y')}  for lead in Data ]
    try:
        data = [lead for lead in data if not lead['Are you looking to buy']]
    except:
        pass
    return render_template('admin/leads-list.html', leads=data, type="seller", LeadType="All Seller Leads", sort="All")


@admin_bp.route('/all/properties')
def all_properties():
    data = PropertyData.fetch_all()
    return render_template('admin/property-list.html', properties=data, ListTitle="Our Properties")

@admin_bp.route('/all/properties/<property_id>')
def property(property_id):
    return redirect(url_for('property', property_id=property_id))

@admin_bp.route('/create/properties', methods=["POST", "GET"])
def create_properties():
    if request.method == "GET":
        return render_template('admin/cu-property.html', title=f"Create New Property")
    else:
        parmas = ['property_name', 'property_addy', 'property_price', 'property_arv', 'property_summary', 'listingPrivacy', 'property_sqft', 'property_type', 'property_parking', 'property_year', 'property_lot', 'property_bedrooms', 'property_bathroom', 'property_half_bathroom', 'ShowingThingy']
        form_data = {param: request.form.get(param) for param in parmas}
        missing_params = [param for param in parmas if not request.form.get(param) or request.form.get(param) == "None"]
        if request.form.get('ShowingThingy') == "True":
            form_data['ShowingThingy'] = True
        else:
            form_data['ShowingThingy'] = False

        if missing_params:
            return render_template('admin/cu-property.html', error=f"Missing Params: {missing_params}, Please Upload Your Images once again, the form would have cleared.", **form_data)
        
        BuildingData = ['property_sqft', 'property_type', 'property_parking', 'property_year', 'property_lot', 'property_bedrooms', 'property_bathroom', 'property_half_bathroom']
        BuildingData = [request.form.get(values) for values in BuildingData]

        Pid = PropertyData.CreateEntry(
            request.form.get('property_name'),
            request.form.get('property_addy'),
            request.form.get('property_price'),
            request.form.get('property_arv'),
            BuildingData,
            session.get('username'),
            request.form.get('property_summary'),
            None,
            request.form.get('property_addy'),
            request.form.get('ShowingThingy')
        )
     
        image_dir = f'property_data/{Pid}/'
        os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
        
        files = request.files.getlist('images')
        for i, file in enumerate(files):
            if file and file.filename:
                filename = f"{i+1}.png"
                file_path = os.path.join(image_dir, filename)
                file.save(file_path)
                print(f"Saved file: {filename}")

        message = (
            f"New Property created using admin panel at {request} on {datetime.now()}\n\n"
            f"Created By:\n{session.get('username')}\n\n"
            f"Property Id:\n{Pid}"
        )
        SendMessage(message)
        return redirect(url_for('admin.all_properties'))

@admin_bp.route('/update/properties/<property_id>', methods=["POST", "GET"])
def update_properties(property_id):
    if request.method == "GET":
        data = PropertyData.fetch_pid(int(property_id))
        data_values = data.get('data', [])
        parmas = {'property_name': data['title'],'property_addy': data['location'],'property_price': data['price'],'property_arv': data['arv'],'property_summary': data['summary'],'listingPrivacy': 'public' if data['is_active'] else 'private','property_sqft': data_values[0],'property_type': data_values[1],'property_parking': data_values[2],'property_year': data_values[3],'property_lot': data_values[4],  'property_bedrooms': data_values[5],'property_bathroom': data_values[6],'property_half_bathroom': data_values[7],}
        form_data = {key: parmas[key] for key in parmas}
        return render_template('admin/cu-property.html', **form_data, title=f"Update Property", instructions="yes")
        
    else:
        parmas = ['property_name', 'property_addy', 'property_price', 'property_arv', 'property_summary', 'listingPrivacy', 'property_sqft', 'property_type', 'property_parking', 'property_year', 'property_lot', 'property_bedrooms', 'property_bathroom', 'property_half_bathroom', 'ShowingThingy']
        form_data = {param: request.form.get(param) for param in parmas}
        missing_params = [param for param in parmas if not request.form.get(param) or request.form.get(param) == "None"]
        if missing_params:
            return render_template('admin/cu-property.html', error=f"Missing Params: {missing_params}, Please Upload Your Images once again, the form would have cleared.", **form_data, title=f"Update Property")
        if request.form.get('ShowingThingy') == "True":
            form_data['ShowingThingy'] = True
        else:
            form_data['ShowingThingy'] = False

        BuildingData = ['property_sqft', 'property_type', 'property_parking', 'property_year', 'property_lot', 'property_bedrooms', 'property_bathroom', 'property_half_bathroom']
        BuildingData = [request.form.get(values) for values in BuildingData]

        PropertyData.UpdateEntry(
            int(property_id),
            request.form.get('property_name'),
            request.form.get('property_addy'),
            request.form.get('property_price'),
            request.form.get('property_arv'),
            BuildingData,
            request.form.get('property_summary'),
            None,
            request.form.get('property_addy'),  
            request.form.get('ShowingThingy'),
            session.get('username')
        )
     
        image_dir = f'property_data/{property_id}/'
        os.makedirs(image_dir, exist_ok=True)

        files = request.files.getlist('images')
        for i, file in enumerate(files):
            if file and file.filename:
                filename = f"{i+1}.png"
                file_path = os.path.join(image_dir, filename)
                file.save(file_path)
                print(f"Saved file: {filename}")

        message = (
            f"Property updated using admin panel at {request} on {datetime.now()}\n\n"
            f"Updated By:\n{session.get('username')}\n\n"
            f"Property Id:\n{property_id}"
        )
        SendMessage(message)
        return redirect(url_for('admin.all_properties'))


@admin_bp.route('/all/api_reqs')
def fetch_twillo_logs():
    messages = FetchLogs()
    return render_template('admin/api/order-list.html', api_logs=messages, log_type="Api")

@admin_bp.route('/all/url_resp')
def url_resp():
    data = URLTrack.ListAll()
    return render_template('admin/api/order-list.html', url_data=data, log_type="url")

@admin_bp.route('/view_more/url_track/<page_for>')
def view_more_url_track(page_for):
    data = URLTrack.ListByPage(page_for)
    property_data = PropertyData.fetch_pid(int(data[0].get('Property_id')))
    lead_data = Leads.ListById(page_for)
    return render_template('admin/api/order-details.html', url_data=data, prop_data=property_data, ld_data=lead_data, count_url=len(data))
