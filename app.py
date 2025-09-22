from flask import *
from database import *
from admin import admin_bp
from admin_utils import Util
from admin_extras import Extras
from admin_export import Export
from admin_auth import auth
from helpers import SendMessage
import os

app = Flask(__name__)
app.secret_key = "dbe38837e035b8dd17d4877d5b77ac5e"
app.register_blueprint(admin_bp)
app.register_blueprint(Util)
app.register_blueprint(Extras)
app.register_blueprint(Export)
app.register_blueprint(auth)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        form_data = request.form.to_dict()
        missing_params = []
        if not form_data.get("phone"):
            missing_params.append("Phone Number")

        if not form_data.get("addy") and not form_data.get("budget"):
            missing_params.append("Address or Budget")

        if missing_params:
            return render_template(
                "index.html",
                error=f"Missing parameters: {missing_params}",
                phone=form_data.get("phone"),
                addy=form_data.get("addy"),
                budget=form_data.get("budget"),
            )
        else:
            try:
                entry = PartialLeads.CreateEntry(
                    form_data.get("phone"),
                    form_data.get("addy"),
                    request.headers.get("X-Forwarded-For"),
                )
                message = (
                    f"New Lead entry using {request} on {datetime.now()}\n\n"
                    f"Lead Phone: {form_data.get("phone")}\n\n"
                    f"Lead Id:\n{entry}\n\n"
                    f"Log on to admin panel at https://amecohomes.com/admin/pending/partial_leads to know more"
                )
                SendMessage(message)
                return redirect(
                    url_for(
                        "fillmore",
                        phone=form_data.get("phone"),
                        addy=form_data.get("addy"),
                        success=True,
                        id=entry,
                    )
                )
            except Exception as e:
                return render_template(
                    "index.html",
                    error=f"An error occurred: {e}",
                    phone=form_data.get("phone"),
                    addy=form_data.get("addy"),
                    budget=form_data.get("budget"),
                )


@app.route("/fill_more", methods=["GET"])
def fill_more_2():
    return render_template("fillmore-2.html", step_1="yes")


@app.route("/form/submit/1", methods=["POST"])
def form_submit_1():
    form_data = request.form.to_dict()
    # params = ["fullname", "desc", "email", "phone", "addy", "cons", "prop_alrdy_listed", "property_owner", "wehn_sell", "looking_to_buy"]
    params = ["addy", "cons"]
    missing_params = [param for param in params if not form_data.get(param)]
    if missing_params:
        return render_template(
            "fillmore-2.html", step_1="yes", error=f"Missing Params: {missing_params}"
        )

    session["form_data"] = [form_data]
    return render_template("fillmore-2.html", step_2="yes", addy=form_data.get("addy"))


@app.route("/form/submit/2", methods=["POST"])
def form_submit_2():
    form_data = request.form.to_dict()
    # params = ["fullname", "desc", "email", "phone", "addy", "cons", "prop_alrdy_listed", "property_owner", "wehn_sell", "looking_to_buy"]
    params = ["fullname", "email", "phone"]
    missing_params = [param for param in params if not form_data.get(param)]
    if not session["form_data"]:
        return redirect(url_for("fill_more_2"))
    if missing_params:
        return render_template(
            "fillmore-2.html", step_2="yes", error=f"Missing Params: {missing_params}"
        )

    form_data_old = session["form_data"]
    form_data_old.append(form_data)
    session["form_data"] = form_data_old
    return render_template(
        "fillmore-2.html", step_3="yes", addy=session["form_data"][0].get("addy")
    )


@app.route("/form/submit/3", methods=["POST"])
def form_submit_3():
    form_data = request.form.to_dict()
    params = [
        "prop_alrdy_listed",
        "property_owner",
        "wehn_sell",
        "looking_to_buy",
        "desc",
    ]
    missing_params = [
        param
        for param in params
        if not form_data.get(param) or form_data.get(param) == "None"
    ]
    if not session["form_data"]:
        return redirect(url_for("fill_more_2"))

    if missing_params:
        return render_template(
            "fillmore-2.html", step_3="yes", error=f"Missing Params: {missing_params}"
        )

    form_data_dict = session.get("form_data")
    try:
        form_data_ = form_data_dict[0]
    except:
        return redirect(url_for("fill_more_2"))
    addy = form_data_.get("addy")    
    try:
        form_data_ = form_data_dict[1]
    except:
        return redirect(url_for("fill_more_2"))

    fullname = form_data_.get("fullname")
    email = form_data_.get("email")
    phone = form_data_.get("phone")
    # this data comes from here in this req
    desc = form_data.get("desc")
    prop_alrdy_listed = form_data.get("prop_alrdy_listed")
    property_owner = form_data.get("property_owner")
    wehn_sell = form_data.get("wehn_sell")
    looking_to_buy = form_data.get("looking_to_buy")

    Leads.CreateEntry(
        None,
        False,
        fullname,
        desc,
        email,
        phone,
        addy,
        request.headers.get("X-Forwarded-For"),
        prop_alrdy_listed,
        property_owner,
        wehn_sell,
        looking_to_buy,
    )
    return render_template("fillmore-2.html", step_4="yes")


@app.route("/fill_more/<phone>/<addy>/<success>/<id>", methods=["GET"])
def fillmore(phone, addy, success, id):
    try:
        id = int(id)
    except:
        return redirect(url_for("fill_more_2"))

    return redirect(url_for("fill_more_2"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/property_data/<path:filename>")
def property_data(filename):
    if not filename.endswith((".png")):
        return "Not Found", 404
    return send_from_directory("property_data", filename)


@app.route("/properties/<property_id>")
def property(property_id):
    data = PropertyData.fetch_pid(property_id)
    if not data:
        return "Not Found", 404
    if data.get("is_active") == "False":
        return "Property Gone", 404
    try:
        images_path = f"property_data/{property_id}"
        images = [
            f"{images_path}/{file}"
            for file in os.listdir(images_path)
            if file.endswith((".png"))
        ]
        images = sorted(images)
        data["images"] = images
    except:
        # going to error page
        return "Not Found", 404

    return render_template("property-detail.html", property=data)

@app.route("/properties/ref/<int:page_id>/<int:page_for>")
def property_ref(page_id, page_for):
    URL_DECODE = URLTrack.fetch_pid(page_id, page_for, request.headers.get("X-Forwarded-For"))
    if not URL_DECODE:
        return "Not Found", 404
    
    return redirect(url_for("property", property_id=URL_DECODE.get("Property_id")))
 

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
