"""
File Name: Database
File Stack: Mongo DB
Language: Python3
"""

from pymongo import MongoClient 
from config import SystemConfig
from datetime import datetime
import certifi, uuid

ca = certifi.where()
client = MongoClient(SystemConfig.db_url, tlsCAFile=ca)

db = client['SiteData']

class Status:
    def check_ping():
        try:
            resp = client.server_info()
            return resp
        except Exception as e:
            return e
    
    def retrive_collections():
        collections = db.list_collection_names()
        return collections
    
    def retrive_data_from(collectionsname):
        data = db[collectionsname].find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data


""" 
Table: Partial Leads
|-----------------------------------------------------------------------------------------------------------------------------------------|
| LeadID | Phone       | Address            | IPV4           | Datetime             | Lead Status  | Next Retry           | Requested Dnd |
|--------|-------------|--------------------|----------------|----------------------|--------------|----------------------|---------------|
| int    | string      | string             | string         | datetime             | string       | datetime             | boolean       |
| 1      | 9876543210  | 123 Maple St, NY   | 192.168.1.1    | 2024-07-13 10:00:00  | New          | 2024-07-14 10:00:00  | false         |
| 2      | 8765432109  | 456 Oak St, LA     | 192.168.1.2    | 2024-07-13 11:00:00  | Contacted    | 2024-07-14 11:00:00  | true          |
| 3      | 7654321098  | 789 Pine St, SF    | 192.168.1.3    | 2024-07-13 12:00:00  | Follow-up    | 2024-07-14 12:00:00  | false         |
| 4      | 6543210987  | 321 Birch St, TX   | 192.168.1.4    | 2024-07-13 13:00:00  | Closed       | 2024-07-14 13:00:00  | true          |
|-----------------------------------------------------------------------------------------------------------------------------------------|
"""


class PartialLeads:
    collection = db['leads']
    @staticmethod
    def CreateEntry(phone, addy, ipady):
        entry = {
            "LeadID": uuid.uuid4().int % 10**10,
            "Phone": phone,
            "Address": addy,
            "IPV4": ipady,
            "Datetime": datetime.now(),
            "Lead Status": "Partial",
            "Next Retry": None,
            "Requested Dnd": False,
            "Admin_Resp": False
        }
        PartialLeads.collection.insert_one(entry)
        return int(entry['LeadID'])
    
    @staticmethod
    def ListAll():
        data = PartialLeads.collection.find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data

    @staticmethod
    def ListById(LeadId):
        data = PartialLeads.collection.find_one({"LeadID": int(LeadId)})
        return data
    


""" 
Table: Full Leads
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NewLeadId   | PartialLeadId  | CameFromRedirect | FullName          | Description                     | Email                | PhoneNumber | Address            | Consented | DND     | NextRetry            | Status     | Notes                        |
|-------------|----------------|------------------|-------------------|---------------------------------|----------------------|-------------|--------------------|-----------|---------|----------------------|------------|------------------------------|
| int (10)    | int (10)       | boolean          | string            | string                          | string               | string      | string             | boolean   | boolean | datetime             | string     | string                       |
| 4382273629  | 1234567890     | true             | John Doe          | Interested in product details   | john@example.com     | 9876543210  | 123 Maple St, NY   | true      | false   | 2024-07-14 10:00:00  | New        | Follow up after initial call |
| 1384927485  | 2345678901     | false            | Jane Smith        | Requested pricing information   | jane@example.com     | 8765432109  | 456 Oak St, LA     | true      | true    | 2024-07-14 11:00:00  | Contacted  | Email sent, awaiting reply   |
| 7203847561  | 3456789012     | true             | Michael Johnson   | Needs demo schedule             | michael@example.com  | 7654321098  | 789 Pine St, SF    | false     | false   | 2024-07-14 12:00:00  | Follow-up  | Call back in two days        |
| 5048291057  | 4567890123     | false            | Emily Davis       | Inquired about bulk purchase    | emily@example.com    | 6543210987  | 321 Birch St, TX   | true      | true    | 2024-07-14 13:00:00  | Closed     | Purchase completed           |
| 3729104836  | 5678901234     | true             | David Brown       | Requested technical support     | david@example.com    | 5432109876  | 654 Elm St, IL     | false     | false   | 2024-07-14 14:00:00  | Pending    | Technical support scheduled  |
| 2839104756  | 6789012345     | false            | Susan Wilson      | Asked for product catalog       | susan@example.com    | 4321098765  | 987 Spruce St, WA  | true      | false   | 2024-07-14 15:00:00  | New        | Catalog sent via email       |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
"""

class Leads:
    collection = db['leads_full']
    @staticmethod
    def CreateEntry(partialId, redirect, fullname, desc, email, phonenumber, address, ipv4, prop_alrdy_listed, property_owner, wehn_sell, looking_to_buy):
        entry = {
            "NewLeadId": uuid.uuid4().int % 10**10,
            "PartialLeadId": partialId,
            "CameFromRedirect": redirect,
            "DateEntry": datetime.now(),
            "FullName": fullname,
            "Description": desc,
            "Email": email,
            "PhoneNumber": phonenumber,
            "Address": address,
            "Consented": True,
            "DND": False,
            "NextRetry": None,
            "Status": "New",
            "Notes": None,
            "IPV4": ipv4,
            "Admin_resp": False,
            "Is your property already listed": prop_alrdy_listed,
            "Are you the property owner": property_owner,
            "When are you looking to sell": wehn_sell,
            "Are you looking to buy": looking_to_buy,
            
        }
        Leads.collection.insert_one(entry)
        return True
    
    @staticmethod
    def ListAll():
        data = Leads.collection.find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data
    
    @staticmethod
    def ListById(LeadID):
        data = Leads.collection.find_one({"NewLeadId": int(LeadID)})
        return data
    

""" 
Table: Admin
|----------------------------------------------------------------------------------------------------------------------------|
| userid | FullName         | account created on | username   | password | notes                    | telegram id | priority |
|--------|------------------|--------------------|------------|----------|--------------------------|-------------|----------|
| int    | string           | datetime           | string     | string   | string                   | string      | int      |
| 1      | Alice Johnson    | 2024-01-15         | alicej     | pass1234 | Admin account            | @alicej     | 1        |
| 2      | Bob Smith        | 2024-02-20         | bobsmith   | securepwd| Second admin account     | @bobsmith   | 2        |
| 3      | Carol White      | 2024-03-25         | carolw     | pwd12345 | New admin                | @carolw     | 3        |
| 4      | David Brown      | 2024-04-30         | davidb     | mypass678| Senior admin             | @davidb     | 4        |
| 5      | Emily Davis      | 2024-05-15         | emilyd     | davis2024| Handles user support     | @emilyd     | 5        |
| 6      | Frank Miller     | 2024-06-10         | frankm     | franky789| Security specialist      | @frankm     | 6        |
|----------------------------------------------------------------------------------------------------------------------------|
"""

class Admin:
    collections = db["admin_data"]
    @staticmethod
    def CreateEntry(fullname, username, password, telegram_id):
        entry = {
            "userid": uuid.uuid4().int % 10**10,
            "FullName": fullname,
            "account created on": datetime.now(),
            "username": username,
            "password": password,
            "notes": None,
            "telegram id": telegram_id,
            "priority": 5
        }
        Admin.collections.insert_one(entry)
        return True
    
    @staticmethod
    def ListAll():
        data = Admin.collections.find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data
    
    @staticmethod
    def ListById(userid):
        data = Admin.collections.find_one({"userid": int(userid)})
        return data
    
    @staticmethod
    def Authorize(username, password):
        data = Admin.collections.find_one({"username": username, "password": password})
        return data
    
"""
Table: URL TRACK
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| URL ID | Url Link                           | Response To (LeadID) | Response Status (Visited, Not Visited) | Form Data               | Notes                   |
|--------|------------------------------------|----------------------|----------------------------------------|-------------------------|-------------------------|
| int    | string                             | int                  | string                                 | string                  | string                  |
| 1      | http://example.com/track1          | 4382273629           | Visited                                | {"name": "John Doe"}    | First response received |
| 2      | http://example.com/track2          | 1384927485           | Not Visited                            | {"name": "Jane Smith"}  | Awaiting response       |
| 3      | http://example.com/track3          | 7203847561           | Visited                                | {"name": "Michael J"}   | Followed up via email   |
| 4      | http://example.com/track4          | 5048291057           | Not Visited                            | {"name": "Emily Davis"} | Resend link             |
| 5      | http://example.com/track5          | 3729104836           | Visited                                | {"name": "David Brown"} | Contacted support       |
| 6      | http://example.com/track6          | 2839104756           | Not Visited                            | {"name": "Susan Wilson"}| Waiting for reply       |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
"""    

class URLTrack:
    collection = db['url_track']
    @staticmethod
    def CreateEntry(response_to, property_id):
        page_id = uuid.uuid4().int % 10**10
        entry = {
            "page_id": page_id,
            "page_link": f"{SystemConfig.base_url}/properties/ref/{page_id}/{response_to}",
            "page_for": response_to,
            "page_status": "Not Visited",
            "Form Data": None,
            "Notes": None,
            "Property_id": property_id,
            "CreatedOn": datetime.now(),
            "FirstVistOn": None,
            "LastVisitOn": None
        }
        URLTrack.collection.insert_one(entry)
        return entry
    
    @staticmethod
    def fetch_pid(pid, page_for, RequestedByIP):
        org_data = URLTrack.collection.find_one({"page_id": pid, "page_for": page_for})
        
        data = URLTrack.collection.find_one({"page_id": int(pid)})
        if not data:
            return False
        
        if data["Form Data"] == None:
            data["Form Data"] = [RequestedByIP]
        else:
            data["Form Data"].append(RequestedByIP)

        if data['FirstVistOn'] == None:
            data['FirstVistOn'] = datetime.now()
        data['LastVisitOn'] = datetime.now()
        data['page_status'] = "Visited"
        URLTrack.collection.update_one({"page_id": int(pid)}, {"$set": data})
        return org_data
    
    def ListAll():
        data = URLTrack.collection.find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data
    
    @staticmethod
    def ListByPage(page_id):
        data = URLTrack.collection.find({"page_for": int(page_id)})
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data


    

""" 
Table: Property Data
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PropertyID | Property Title        | Location          | Price   | Arv     | Data                                                                                                                                                                    | Pictures Path       | Summary                          | Details                         | map data                                                                                                                       |
|------------|-----------------------|-------------------|---------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|----------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| int        | string                | string            | float   | float   | array                                                                                                                                                                   | string              | string                           | string                          | array                                                                                                                          |
| 1          | Cozy Family Home      | New York, NY      | 500000  | 600000  | {"Sq. Footage": 1713, "Type": "Single-Family", "Parking": "Driveway", "Year build": 1960, "Lot size": "0.17 acres", "Bedrooms": 4, "Bathrooms": 3, "Half Bathrooms": 0} | /images/property1   | Ideal for a small family         | Spacious living area and garden | {"co_ords": "11.02828282,16.920982", "apple maps link": "applemaps.com/sjsks", "googlemaps link": "googlemaps.com/sjsjs"}      |
| 2          | Modern Apartment      | Los Angeles, CA   | 750000  | 850000  | {"Sq. Footage": 2000, "Type": "Condo", "Parking": "Garage", "Year build": 2015, "Lot size": "0.2 acres", "Bedrooms": 3, "Bathrooms": 2, "Half Bathrooms": 1}            | /images/property2   | Modern amenities included        | Close to downtown               | {"co_ords": "12.345678,98.765432", "apple maps link": "applemaps.com/xyz", "googlemaps link": "googlemaps.com/xyz"}            |
| 3          | Suburban House        | San Francisco, CA | 650000  | 700000  | {"Sq. Footage": 1800, "Type": "Single-Family", "Parking": "Street", "Year build": 1985, "Lot size": "0.15 acres", "Bedrooms": 3, "Bathrooms": 2, "Half Bathrooms": 0}   | /images/property3   | Great neighborhood               | Near schools and parks          | {"co_ords": "13.456789,87.654321", "apple maps link": "applemaps.com/abc", "googlemaps link": "googlemaps.com/abc"}            |
| 4          | Downtown Loft         | Chicago, IL       | 850000  | 950000  | {"Sq. Footage": 2200, "Type": "Loft", "Parking": "Garage", "Year build": 2000, "Lot size": "0.1 acres", "Bedrooms": 2, "Bathrooms": 1, "Half Bathrooms": 1}             | /images/property4   | Perfect for young professionals  | Walking distance to amenities   | {"co_ords": "14.567890,76.543210", "apple maps link": "applemaps.com/def", "googlemaps link": "googlemaps.com/def"}            |
| 5          | Beachside Villa       | Miami, FL         | 1200000 | 1300000 | {"Sq. Footage": 2500, "Type": "Villa", "Parking": "Private", "Year build": 1995, "Lot size": "0.5 acres", "Bedrooms": 5, "Bathrooms": 4, "Half Bathrooms": 1}           | /images/property5   | Luxury living by the sea         | Includes a private beach        | {"co_ords": "15.678901,65.432109", "apple maps link": "applemaps.com/ghi", "googlemaps link": "googlemaps.com/ghi"}            |
| 6          | Countryside Cottage   | Austin, TX        | 400000  | 450000  | {"Sq. Footage": 1600, "Type": "Cottage", "Parking": "Driveway", "Year build": 1970, "Lot size": "0.3 acres", "Bedrooms": 3, "Bathrooms": 2, "Half Bathrooms": 0}        | /images/property6   | Cozy and charming                | Beautiful rural setting         | {"co_ords": "16.789012,54.321098", "apple maps link": "applemaps.com/jkl", "googlemaps link": "googlemaps.com/jkl"}            |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
"""

class PropertyData:
    collection = db['property_data']
    @staticmethod
    def CreateEntry(title, location, price, arv, data, admin_username, summary, notes, map_data, ShowingThingy):
        pid = uuid.uuid4().int % 10**10

        entry = {
            "PropertyID": pid,
            "title": title,
            "location": location,
            "is_active": ShowingThingy, # True -> Yes, False -> No
            "price": price,
            "arv": arv,
            "data": data,
            "images_path": f"/property_data/{pid}",
            "summary": summary,
            "notes": notes,
            "map_data": map_data,
            "property_created_on": datetime.now(),
            "property_last_updated": None,
            "property_created_by": admin_username,
            "property_last_updated_by": None
        }
        PropertyData.collection.insert_one(entry)
        return pid
    
    @staticmethod
    def fetch_pid(pid):
        data = PropertyData.collection.find_one({"PropertyID": int(pid)})
        return data
    
    @staticmethod
    def fetch_all():
        data = PropertyData.collection.find()
        Clean_Data = []
        for i in data:
            Clean_Data.append(i)
        return Clean_Data
    
    @staticmethod
    def UpdateEntry(pid, title, location, price, arv, building_data, summary, notes, map_data, showing_thing, admin_username):
        property_data = PropertyData.collection.find_one({"PropertyID": int(pid)})    
        if not property_data:
            return False

        update_data = {
            'title': title,
            'location': location,
            'price': price,
            'arv': arv,
            'data': building_data,
            'summary': summary,
            'notes': notes,
            'map_data': map_data,
            'property_last_updated': datetime.now(),
            'property_last_updated_by': admin_username,
            'is_active': showing_thing
        }

        PropertyData.collection.update_one({"PropertyID": int(pid)}, {"$set": update_data})
        return True
    

""" 
Feature: Function For Fetching Data:
Params: PhoneNumber, Fullname, address, propertyname. 
"""