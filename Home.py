import os
import uuid
from doctest import debug
from flask import Flask, render_template, request, session, redirect, flash, send_file,url_for
from flask.sessions import SecureCookieSession

from werkzeug.utils import secure_filename
from DBConnection import Db
import datetime
from datetime import datetime
from datetime import date 

import requests
import razorpay

from textblob import TextBlob

app = Flask(__name__, template_folder='template', static_url_path='/static/')

app.secret_key = "asdff"


@app.route('/')
def ind():
    return render_template("HomePage.html")


@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")


@app.route('/Login')
def login():
    return render_template("login.html")


@app.route('/Adminhome')
def Adminhome():
    return render_template("Adminhome.html")


@app.route('/Villagehome')
def Villagehome():
    return render_template("Tribal/Villagehome.html")

@app.route('/Userhome')
def Userhome():
    return render_template("User/Userhome.html")

@app.route('/LogOut')
def logOut():
    return render_template("LogOut.html")


@app.route('/login1', methods=['post'])
def login1():
    name = request.form['un']
    password = request.form['pass']
    session['lid'] = name
    qry = "select * from login where admin_id='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        return Adminhome()
    qry = "select * from village_registration where village_id='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        status = res['status']
        vid = res['idvillage_registration']
        session['vid'] = vid
        if status == 'requested':
            return "<script>alert('Pending please wait');window.location='/';</script>"
        elif status == 'rejected':
            return "<script>alert('Your Request Rejected');window.location='/';</script>"
        elif status == 'approved':
            return Villagehome()
    qry = "select * from user_register where user_id='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        session['uid'] = name
        return "<script>alert('WELCOME "+name+"');window.location='/Userhome';</script>"
    return "<script>alert('invalid');window.location='/';</script>"


@app.route('/LinkAddVillage')
def LinkAddVillage():
    ob = Db()
    data = None
    res = ob.select("select * from district")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('AddVillage.html', data=res)


@app.route('/VillageRegistration', methods=['post'])
def VillageRegistration():
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    pincode = request.form['TxtPincode']
    latitude = request.form['TxtLatitude']
    longitude = request.form['TxtLongitude']
    districtid = request.form['TxtDistrict']
    villageid = request.form['TxtUsername']
    password = request.form['TxtPassword']
    print("1")
    ob = Db()
    q = "insert into village_registration values(null,'" + name + "','" + address + "','" + latitude + "','" + longitude + "','" + pincode + "','" + districtid + "','" + password + "','" + villageid + "','requested' )"
    print(q)
    ob.insert(q)
    return "<script>alert('Inserted successfully');window.location='/Login';</script>"


@app.route('/LinkAddUser')
def LinkAddUser():
    return render_template('AddUser.html')


@app.route('/UserRegistration', methods=['post'])
def UserRegistration():
    user_id = request.form['TxtUserid']
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    phone = request.form['TxtPhone']
    password = request.form['TxtPassword']
    ob = Db()
    qry = ob.selectOne("select * from login where admin_id = '" + str(user_id) + "'")
    res = ob.selectOne(qry)
    if res == None:
        qry = ob.selectOne("select * from village_registration where village_id = '" + str(user_id) + "'")
        res = ob.selectOne(qry)
        if res == None:
            qry = ob.selectOne("select * from user_register where user_id = '" + str(user_id) + "'")
            res = ob.selectOne(qry)
            if res == None:
                q = "insert into user_register values('"+str(user_id)+"','" + name + "','" + address + "','" + phone + "','"+ password + "')"
                ob.insert(q)
                return "<script>alert('Inserted succesfully');window.location='/Login';</script>"
    return "<script>alert('User_id  already exist add unique one ');window.location='/LinkAddUser';</script>"




# ---------------------------------------Admin-----------------------------------------#
@app.route('/ViewVillageRequest')
def ViewVillageRequest():
    ob = Db()
    data = None
    res = ob.select(
        "select v.*,d.name as district from village_registration as v join district as d on d.iddistrict=v.iddistrict where v.status='requested'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewVillageRequest.html', data=res)


@app.route('/Location')
def ViewLocation():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    return render_template("ViewLocation.html", lon=lon, lat=lat)


@app.route('/approveVillage')
def approveVillage():
    id = request.args.get('id')
    ob = Db()
    q = "update village_registration set status='approved' where idvillage_registration='" + id + "'"
    ob.update(q)
    return "<script>alert('Approved succesfully');window.location='/Adminhome';</script>"


@app.route('/RejectVillage')
def RejectVillage():
    id = request.args.get('id')
    ob = Db()
    q = "update village_registration set status='rejected' where idvillage_registration='" + id + "'"
    ob.update(q)
    return "<script>alert('Rejected succesfully');window.location='/Adminhome';</script>"


@app.route('/ViewVillageApproved')
def ViewVillageApproved():
    ob = Db()
    data = None
    res = ob.select(
        "select v.*,d.name as district from village_registration as v join district as d on d.iddistrict=v.iddistrict where v.status='approved'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewVillageApproved.html', data=res)


@app.route('/ViewFeedback')
def ViewFeedback():
    ob = Db()
    data = None
    res = ob.select(
        "select f.*,vr.name from feedback as f join village_registration as vr on vr.idvillage_registration=f.idvillage_registration")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    nes = ob.select("select feedback_nltk.*,village_registration.name from feedback_nltk join village_registration where feedback_nltk.user_id = village_registration.idvillage_registration")

    return render_template('ViewFeedback.html', data=res,datanltk =nes)


@app.route('/ViewCulturalActivities')
def ViewCulturalActivities():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from cultural_activities where idvillage_registration='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewCulturalActivities.html', data=res)

@app.route('/Viewadminstay')
def Viewadminstay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from village_stay where idvillage_registration='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('Viewvillagestay.html', data=res)

# ---------------------------------------------------Village--------------------------------------------------#
@app.route('/LinkAddCulturalActivities')
def LinkAddCulturalActivities():
    return render_template("Tribal/AddCulturalActivities.html")


@app.route('/AddCulturalActivities', methods=['post'])
def AddCulturalActivities():
    vid = str(session['vid'])
    name = request.form['TxtName']
    duration = request.form['TxtDuration']
    desc = request.form['TxtDescription']
    amount = request.form['TxtAmount']
    ob = Db()
    q = "insert into cultural_activities values(null,'" + vid + "','" + name + "','" + duration + "','" + desc + "','" + amount + "')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Villagehome';</script>"


@app.route('/ViewCulturalActivitiesV')
def ViewCulturalActivitiesV():
    vid = str(session['vid'])
    ob = Db()
    data = None
    res = ob.select("select * from cultural_activities where idvillage_registration='" + vid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewCulturalActivities.html', data=res)



@app.route('/LinkEditActivity')
def LinkEditActivity():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from cultural_activities where idcultural_activities='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/EditCulturalActivities.html', data=res)


@app.route('/EditCulturalActivities', methods=['post'])
def EditCulturalActivities():
    id = request.form['id']
    name = request.form['TxtName']
    duration = request.form['TxtDuration']
    desc = request.form['TxtDescription']
    amount = request.form['TxtAmount']
    ob = Db()
    q = "update cultural_activities set activity_name='" + name + "',duration='" + duration + "',description='" + desc + "',amount='" + amount + "' where idcultural_activities='" + str(id) + "'"
    ob.insert(q)
    return "<script>alert('Updated successfully');window.location='/Villagehome';</script>"

@app.route('/LinkEditStay')
def LinkEditStay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from village_stay where idvillage_stay='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/EditVillageStay.html', data=res)


@app.route('/EditVillageStay', methods=['post'])
def EditVillageStay():
    id = request.form['id']
    desc = request.form['TxtDescription']
    info = request.form['info']
    amount = request.form['TxtAmount']
    ob = Db()
    q = "update village_stay set food_description ='" + desc + "',stay_information ='" + info + "',rate_per_head='" + amount + "' where idvillage_stay ='" + str(id) + "'"
    ob.insert(q)
    return "<script>alert('Updated successfully');window.location='/Villagehome';</script>"




@app.route('/DeleteActivity')
def DeleteActivity():
    id = request.args.get('id')
    ob = Db()
    q = "delete from cultural_activities where idcultural_activities='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted successfully');window.location='/Villagehome';</script>"

@app.route('/LinkUploadImage')
def LinkUploadImage():
    id = request.args.get('id')
    session['cid'] = id
    return render_template("Tribal/UploadImage.html",id =id)

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def save_to_database(file_description, file_type, file_path, cultural_activities_id):
    ob = Db()
    q = "insert into cultural_gallery values(null,'" + cultural_activities_id + "','" + file_description + "','" + file_type + "','" + file_path + "',curdate())"
    ob.insert(q)
@app.route('/uploadimagevideo', methods=['POST'])
def upload_image_video():
    # Extract form data
    file = request.files['TxtImage']
    file_type = request.form['TxtType']
    file_description = request.form['TxtDesc']
    rid = request.form['TxtRid']  # Assuming this is cultural_activities_id

    # Check if file is selected
    if file:
        # Generate a unique filename to prevent overwriting
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Save the file
        file.save(file_path)

        # Modify file_path to remove the folder path
        _, filename_only = os.path.split(file_path)

        # Save file details to the database
        save_to_database(file_description, file_type, filename_only, rid)

        return "<script>alert('File uploaded successfully.');window.location='/Villagehome';</script>"
    else:
        return "<script>alert('No file selected.');window.location='/Villagehome';</script>"




@app.route('/LinkUploadImagestay')
def LinkUploadImagestay():
    id = request.args.get('id')
    session['cid'] = id
    return render_template("Tribal/UploadImagestay.html",id=id)



def save_to_database_stay(file_description, file_type, file_path, village_stay_id):
    ob = Db()
    q = "insert into stay_gallery values(null,'" + village_stay_id + "','" + file_description + "','" + file_type + "','" + file_path + "',curdate())"
    ob.insert(q)
@app.route('/uploadimagevideostay', methods=['POST'])
def upload_image_videostay():
    # Extract form data
    file = request.files['TxtImage']
    file_type = request.form['TxtType']
    file_description = request.form['TxtDesc']
    rid = request.form['TxtRid']  # Assuming this is cultural_activities_id

    # Check if file is selected
    if file:
        # Generate a unique filename to prevent overwriting
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Save the file
        file.save(file_path)

        # Modify file_path to remove the folder path
        _, filename_only = os.path.split(file_path)

        # Save file details to the database
        save_to_database_stay(file_description, file_type, filename_only, rid)

        return "<script>alert('File uploaded successfully.');window.location='/Villagehome';</script>"
    else:
        return "<script>alert('No file selected.');window.location='/Villagehome';</script>"

@app.route('/ViewActivityVideo')
def ViewActivityVideo():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from cultural_gallery where idcultural_activities='" + id + "' and file_type='video'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityVideo.html', data=res)

@app.route('/ViewActivityVideostay')
def ViewActivityVideostay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from stay_gallery where idvillage_stay='" + id + "' and file_type='video'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityVideostay.html', data=res)

@app.route('/ViewActivityImage')
def ViewActivityImage():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from cultural_gallery where idcultural_activities='" + id + "' and file_type='image'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityImage.html', data=res)

@app.route('/ViewActivityImagestay')
def ViewActivityImagestay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from stay_gallery where idvillage_stay='" + id + "' and file_type='image'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityImagestay.html', data=res)

@app.route('/deleteadminvillage')
def deleteadminvillage():
    id = request.args.get('id')
    ob = Db()
    q = "delete from village_registration where idvillage_registration='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"

@app.route('/DeleteImage')
def DeleteImage():
    id = request.args.get('id')
    ob = Db()
    q = "delete from cultural_gallery where idcultural_gallery='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Villagehome';</script>"
@app.route('/DeleteImageStay')
def DeleteImageStay():
    id = request.args.get('id')
    ob = Db()
    q = "delete from stay_gallery where idstay_gallery='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Villagehome';</script>"


@app.route('/LinkPlayVideo')
def LinkPlayVideo():
    id = request.args.get('id')
    session['id'] = id
    return render_template('Tribal/PlayVideo.html')


@app.route('/LinkAddVillageStay')
def LinkAddVillageStay():
    return render_template("Tribal/AddVillageStayy.html")


@app.route('/AddVillageStay', methods=['post'])
def AddVillageStay():
    vid = str(session['vid'])
    desc = request.form['TxtDesc']
    info = request.form['TxtInfo']
    amount = request.form['TxtAmount']
    ob = Db()
    q = "insert into village_stay values(null,'" + vid + "','" + desc + "','" + info + "','" + amount + "')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Villagehome';</script>"


@app.route('/ViewVillageStay')
def ViewVillageStay():
    vid = str(session['vid'])
    ob = Db()
    data = None
    res = ob.select("select * from village_stay where idvillage_registration='" + vid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewVillageStay.html', data=res)


@app.route('/DeleteStay')
def DeleteStay():
    id = request.args.get('id')
    ob = Db()
    q = "delete from village_stay idvillage_stay='" + id + "'"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Villagehome';</script>"


@app.route('/ViewActivityB')
def ViewActivityB():
    vid = str(session['vid'])
    ob = Db()
    data = None
    res = ob.select("select * from cultural_activities where idvillage_registration='" + vid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityBooking.html', data=res)
@app.route('/ViewStayB')
def ViewStayB():
    vid = str(session['vid'])
    ob = Db()
    data = None
    res = ob.select("select * from village_stay where idvillage_registration='" + vid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewStayPBooking.html', data=res)

@app.route('/ViewActivityBooking')
def ViewActivityBooking():
    vid = str(session['vid'])
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select * from cultural_booking where idcultural_activities='" + id + "' and idvillage_registration='" + vid + "' and booking_status='requested'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewActivityBookingRequest.html', data=res)


@app.route('/ApproveActivityBooking')
def ApproveActivityBooking():
    id = request.args.get('id')
    ob = Db()
    q = "update cultural_booking set booking_status='approved' where idcultural_booking='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Villagehome';</script>"


@app.route('/RejectActivityBooking')
def RejectActivityBooking():
    id = request.args.get('id')
    ob = Db()
    q = "update cultural_booking set booking_status='rejected' where idcultural_booking='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Villagehome';</script>"


@app.route('/ViewApprovedBooking')
def ViewApprovedBooking():
    vid = str(session['vid'])
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select * from cultural_booking where idcultural_activities='" + id + "' and idvillage_registration='" + vid + "' and booking_status ='approved'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewApprovedBooking.html', data=res)

@app.route('/ViewPaidABooking')
def ViewPaidABooking():
    vid = str(session['vid'])
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select * from cultural_booking where idcultural_activities='" + id + "' and idvillage_registration='" + vid + "' and booking_status='paid'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewApprovedBooking.html', data=res)

@app.route('/ViewPaidSBooking')
def ViewPaidSBooking():
    vid = str(session['vid'])
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select * from tribal_stay_booking where idvillage_stay ='" + id + "' and status='paid'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewPaidSBooking.html', data=res)


@app.route('/ViewStayBooking')
def ViewStayBooking():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from tribal_stay_booking where idvillage_stay='" + id + "' and status='requested'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewStayBooking.html', data=res)


@app.route('/ApprovedStayBooking')
def ApprovedStayBooking():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from tribal_stay_booking where idvillage_stay='" + id + "' and status='approved'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Villagehome';</script>"
    return render_template('Tribal/ViewApprovedStayBooking.html', data=res)


@app.route('/ApproveStayBooking')
def ApproveStayBooking():
    id = request.args.get('id')
    ob = Db()
    q = "update tribal_stay_booking set status='approved' where idtribal_stay_booking='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Villagehome';</script>"


@app.route('/RejectStayBooking')
def RejectStayBooking():
    id = request.args.get('id')
    ob = Db()
    q = "update tribal_stay_booking set status='rejected' where idtribal_stay_booking='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Villagehome';</script>"

@app.route('/ViewVillageFeedbacks')
def ViewVillageFeedbacks():
    vid = str(session['vid'])
    ob =Db()
    q = "select * from feedback where idvillage_registration ='"+vid+"' and reply ='no reply'"
    req = ob.select(q)
    q = "select * from feedback where idvillage_registration ='" + vid + "' and reply !='no reply'"
    req1 = ob.select(q)
    return render_template('Tribal/feedback.html',data=req,data1=req1)

@app.route('/SendFeedbackReply')
def SendFeedbackReply():
    id = request.args.get('id')
    ob = Db()
    q = "select * from feedback where feedback_id ='"+id+"' and reply ='no reply'"
    res =ob.selectOne(q)
    if res ==None:
        return "<script>alert('No Data Found');window.location='/ViewVillageFeedbacks';</script>"
    return render_template('Tribal/SendFeedback.html',data=res)
@app.route('/VillageSendReplyform', methods=['post'])
def VillageSendReplyform():
    reply = request.form['reply']
    id = request.form['id']
    ob = Db()
    q = "select * from feedback where feedback_id ='" + id + "' and reply ='no reply'"
    res = ob.selectOne(q)
    if res == None:
        return "<script>alert('No Data Found');window.location='/ViewVillageFeedbacks';</script>"
    q = "update feedback set reply ='"+reply+"' where feedback_id ='"+id+"'"
    ob.update(q)
    return redirect(url_for('ViewVillageFeedbacks'))





# user side

@app.route('/UserViewDistrict')
def UserViewDistrict():
    ob = Db()
    q = "select * from district"
    res = ob.select(q)
    return render_template('User/View_district.html', data=res)

@app.route('/UserViewVillage')
def UserViewVillage():
    id = request.args.get('id')
    ob = Db()
    q = "select * from village_registration where iddistrict ='"+str(id)+"' and status ='approved'"
    res = ob.select(q)
    return render_template('User/View_village.html', data =res)
@app.route('/UserLocation')
def UserViewLocation():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    return render_template("User/ViewLocation.html", lon=lon, lat=lat)

@app.route('/UserViewCulturalActivities')
def UserViewCulturalActivities():
    id = request.args.get('id')

    ob = Db()
    data = None
    res = ob.select("select * from cultural_activities where idvillage_registration='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    session['user_view_village_id'] = id
    return render_template('User/ViewCulturalActivities.html', data=res)

@app.route('/UserViewActivityImage')
def UserViewActivityImage():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from cultural_gallery where idcultural_activities='" + id + "' and file_type='image'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewActivityImage.html', data=res)

@app.route('/UserViewActivityImagestay')
def UserViewActivityImagestay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from stay_gallery where idvillage_stay='" + id + "' and file_type='image'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewActivityImagestay.html', data=res)


@app.route('/UserViewActivityVideo')
def UserViewActivityVideo():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from cultural_gallery where idcultural_activities='" + id + "' and file_type='video'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewActivityVideo.html', data=res)

@app.route('/UserViewActivityVideostay')
def UserViewActivityVideostay():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from stay_gallery where idvillage_stay='" + id + "' and file_type='video'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewActivityVideostay.html', data=res)


@app.route('/UserLinkPlayVideo')
def UserLinkPlayVideo():
    id = request.args.get('id')
    session['id'] = id
    return render_template('User/PlayVideo.html')

@app.route('/RequestBookActivity')
def RequestBookActivity():
    id = request.args.get('id')
    ob = Db()
    res = ob.selectOne("select * from cultural_activities where idcultural_activities='" + id + "'")
    amount = res['amount']
    activity = res['activity_name']
    duration = res['duration']
    return render_template('User/RequestBookActivity.html', data=id, amount=amount, activity=activity, duration=duration)


from dateutil import parser
@app.route('/RequestBookActivityform',methods =['post'])
def RequestBookActivityform():
    user_query = request.form['query']
    dates = request.form['date']
    id = request.form['id']
    status = "requested"
    village_id = session['user_view_village_id']
    no_of_people = request.form['no_of_people']
    amount = request.form['ticket_price']
    total = int(no_of_people) * int(amount)

    booking_date = parser.parse(dates).date()
    
    
    today_date = datetime.today().date()
    
   
    if booking_date <= today_date:
        return "<script>alert('Invalid booking date. Please select a future date.');window.location='/Userhome';</script>"
    

    ob = Db()
    q = "select * from cultural_booking where user_id='"+session['uid']+"' and book_date ='"+dates +"' and user_query ='"+user_query+"' and idcultural_activities ='"+id+"' and booking_status ='requested' and idvillage_registration ='"+village_id+"' and no_of_people ='"+no_of_people+"'"
    res =ob.selectOne(q)
    if res == None:
        q = "insert into cultural_booking values(null,'" + session['uid'] + "','" + dates + "','" + user_query + "','" + id + "','" + str(status) + "','" + str(village_id) + "','" + str(no_of_people) + "','" + str(total) + "')"
        ob.insert(q)
        return "<script>alert('Booking request send to village');window.location='/Userhome';</script>"
    return "<script>alert('Booking request already send for the date');window.location='/Userhome';</script>"



@app.route('/ViewBookActivity')
def ViewBookActivity():
    id = request.args.get('id')
    ob = Db()
    q = "select * from cultural_booking join cultural_activities where cultural_booking.user_id ='"+str(session['uid'])+"' and cultural_booking.idcultural_activities ='"+str(id)+"' and cultural_booking.idcultural_activities = cultural_activities.idcultural_activities and cultural_booking.booking_status ='approved'"
    req = ob.select(q)
    q = "select * from cultural_booking join cultural_activities where cultural_booking.user_id ='" + str(session['uid']) + "' and cultural_booking.idcultural_activities ='" + str(id) + "' and cultural_booking.idcultural_activities = cultural_activities.idcultural_activities and cultural_booking.booking_status ='requested'"
    req1 = ob.select(q)
    return render_template('User/ViewBookActivity.html', data=req, data1=req1)


@app.route('/payActivityBooking')
def payActivityBooking():
    id = request.args.get('id')
    ob = Db()
    q = "select * from cultural_booking where idcultural_booking='" + id + "' and booking_status ='approved'"
    res = ob.selectOne(q)
    if res == None:
        return "<script>alert('having some error);window.location='/Userhome';</script>"
    total = res['total']
    a = total
    total = int(total) * 100
    client = razorpay.Client(
        auth=("rzp_test_SROSnyInFv81S4", "WIWYANkTTLg7iGbFgEbwj4BM"))
    session['activityid'] = id
    session['payamounts'] =a
    payment = client.order.create({'amount': total, 'currency': 'INR', 'payment_capture': '1'})
    return render_template('User/activitypayment.html', payment=payment, amount=total, data=id, a=a)

@app.route('/makepaymentactivity')
def makepaymentactivity():
    import datetime
    id = session['activityid']
    ob = Db()
    q = "update cultural_booking set booking_status='paid' where idcultural_booking='" + id + "'"
    ob.update(q)
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    q = "insert into Payment_history values(null,'" + current_datetime + "','" + session['uid'] + "','" + session[
        'payamounts'] + "')"
    ob.insert(q)
    return "<script>alert('Payment succesfull');window.location='/Userhome';</script>"

@app.route('/ViewActivityBookings')
def ViewActivityBookings():
    ob = Db()
    q = "select * from cultural_booking join cultural_activities where cultural_booking.user_id ='" + str(session['uid']) + "' and cultural_booking.idcultural_activities = cultural_activities.idcultural_activities and cultural_booking.booking_status ='paid'"
    req = ob.select(q)
    # q = "select * from cultural_booking join cultural_activities where cultural_booking.user_id ='" + str(session['uid']) + "' and cultural_booking.idcultural_activities = cultural_activities.idcultural_activities and cultural_booking.booking_status ='requested'"
    # req1 = ob.select(q)
    return render_template('User/ViewBookActivityp.html', data=req,)

@app.route('/UserSelectDistrict')
def UserSelectDistrict():
    ob = Db()
    q = "select * from district"
    res = ob.select(q)
    return render_template('User/View_districts.html', data=res)

@app.route('/UserViewVillages')
def UserViewVillages():
    id = request.args.get('id')
    ob = Db()
    q = "select * from village_registration where iddistrict ='"+str(id)+"' and status ='approved'"
    res = ob.select(q)
    return render_template('User/View_villages.html', data =res)

@app.route('/UserVillageStay')
def UserVillageStay():
    id = request.args.get('id')
    ob = Db()
    q = "select * from village_registration join village_stay where village_registration.idvillage_registration ='"+str(id)+"' and village_registration.idvillage_registration = village_stay.idvillage_registration"
    res = ob.select(q)
    return render_template('User/ViewVillageStay.html', data =res)


@app.route('/UserBookStay')
def UserBookStay():
    id = request.args.get('id')
    ob = Db()
    q = "select * from village_stay where idvillage_stay ='" + str(id) + "'"
    res = ob.selectOne(q)
    stay_rate = res['rate_per_head']
    return render_template('User/RequestBookStay.html',rate=stay_rate,data=id)

@app.route('/RequestBookStayform',methods =['post'])
def RequestBookStayform():
    user_query = request.form['query']
    dates = request.form['date']
    booking_date = parser.parse(dates).date()
    
    # Get today's date
    today_date = datetime.today().date()
    
    # Check if the booking date is not today or any previous day
    if booking_date <= today_date:
        return "<script>alert('Invalid booking date. Please select a future date.');window.location='/Userhome';</script>"
    
    id = request.form['id']
    status = "requested"
    no_of_people = request.form['no_of_people']
    amount = request.form['ticket_price']
    total = int(no_of_people) * int(amount)
    ob = Db()
    q = "select * from tribal_stay_booking  where idvillage_stay ='" + str(id) + "' and user_id ='"+session['uid']+"' and book_date ='"+str(dates)+"' and status ='requested' and number_of_people ='"+str(no_of_people)+"' and user_query ='"+str(user_query)+"' "
    print(q)
    res = ob.selectOne(q)
    if res == None:
        q = "insert into tribal_stay_booking values(null,'" + id + "','" + session['uid'] + "','" + dates + "','" + user_query + "','" + str(status) + "','"+str(no_of_people)+"','"+str(total)+"')"
        ob.insert(q)
        return "<script>alert('Booking request send to village');window.location='/Userhome';</script>"
    return "<script>alert('Booking request already send for the date');window.location='/Userhome';</script>"

@app.route('/ViewBookStay')
def ViewBookStay():
    id = request.args.get('id')
    ob = Db()
    q = "select * from tribal_stay_booking join village_stay where tribal_stay_booking.idvillage_stay ='" + str(id) + "' and village_stay.idvillage_stay = tribal_stay_booking.idvillage_stay and tribal_stay_booking.status ='requested' and tribal_stay_booking.user_id ='"+str(session['uid'])+"'"
    req = ob.select(q)
    q = "select * from tribal_stay_booking join village_stay where tribal_stay_booking.idvillage_stay ='" + str(id) + "' and village_stay.idvillage_stay = tribal_stay_booking.idvillage_stay and tribal_stay_booking.status ='approved' and tribal_stay_booking.user_id ='"+str(session['uid'])+"'"
    req1 = ob.select(q)
    # q = "select * from tribal_stay_booking join village_stay where tribal_stay_booking.idvillage_stay ='" + str(id) + "' and village_stay.idvillage_stay = tribal_stay_booking.idvillage_stay and tribal_stay_booking.status ='rejected' and tribal_stay_booking.user_id ='"+str(session['uid'])+"'"
    # req1 = ob.select(q)
    return render_template('User/ViewBookStay.html', data=req, data1=req1)
@app.route('/payStayBooking')
def payStayBooking():
    id = request.args.get('id')
    ob = Db()
    q = "select * from tribal_stay_booking where idtribal_stay_booking='"+id+"' and status ='approved'"
    res = ob.selectOne(q)
    if res ==None:
        return "<script>alert('having some error);window.location='/Userhome';</script>"
    total = res['total']
    a = total
    total = int(total)* 100
    client = razorpay.Client(
        auth=("rzp_test_SROSnyInFv81S4", "WIWYANkTTLg7iGbFgEbwj4BM"))
    session['stayid'] = id
    session['payamount'] =a
    payment = client.order.create({'amount': total, 'currency': 'INR', 'payment_capture': '1'})
    return render_template('User/staypayment.html', payment=payment, amount=total,data=id,a=a)


@app.route('/makepaymentstay', methods =['post'])
def makepaymentstay():
    id = session['stayid']
    ob = Db()
    q = "update tribal_stay_booking set status='paid' where idtribal_stay_booking='" + id + "'"
    ob.update(q)

    q = "insert into Payment_history values(null,curdate(),'"+session['uid']+"','"+session['payamount']+"')"
    ob.insert(q)
    return "<script>alert('Payment succesfull');window.location='/Userhome';</script>"


@app.route('/ViewStayBookings')
def ViewStayBookings():
    ob = Db()
    q = "select * from tribal_stay_booking join village_stay where village_stay.idvillage_stay = tribal_stay_booking.idvillage_stay and tribal_stay_booking.status ='paid' and tribal_stay_booking.user_id ='" + str(session['uid']) + "'"
    req = ob.select(q)

    return render_template('User/ViewBookStayp.html', data=req)

@app.route('/ViewUserHistory')
def ViewUserHistory():
    ob =Db()
    q = "select * from Payment_history where user_id ='"+session['uid']+"'"
    req = ob.select(q)
    return render_template('User/ViewUserHistory.html',data=req)


@app.route('/UserFeedbacks')
def UserFeedbacks():
    id = request.args.get('id')
    ob = Db()
    q = "select * from feedback where user_id ='"+session['uid']+"' and idvillage_registration='"+id+"'"
    req = ob.select(q)
    a = "select * from village_registration where idvillage_registration ='"+id+"'"
    res = ob.selectOne(a)
    name = res['name']

    return render_template('User/feedback.html',data=req,id=name)
@app.route('/UserSendFeedback')
def UserSendFeedback():
    id = request.args.get('id')
    ob = Db()
    a = "select * from village_registration where idvillage_registration ='" + id + "'"
    res = ob.selectOne(a)
    name = res['name']
    return render_template('User/SendFeedback.html',id=id,name=name)

@app.route('/UserSendFeedbackform', methods =['post'])
def UserSendFeedbackform():
    desc = request.form['description']
    id = request.form['id']
    ob = Db()
    q = "insert into feedback values(null,'"+session['uid']+"','"+id+"', '"+desc+"','no reply',curdate())"
    ob.insert(q)
    obj = TextBlob(desc)
    sentiment = obj.sentiment.polarity
    print(sentiment)
    if sentiment == 0:
        print('The text is neutral')
    elif sentiment > 0:
        print('The text is positive')
        a = "select * from feedback_nltk where user_id ='"+id+"'"
        pins = ob.selectOne(a)
        # cursor = connection.cursor()
        # cursor.execute("select * from feedback_nltk where to_user_id='" + to_user_id + "' ")
        # pins = cursor.fetchone()
        if pins == None:
            q = "insert into feedback_nltk values(null,1,0,'"+id+"')"
            ob.insert(q)
            # cursor = connection.cursor()
            # cursor.execute("insert into feedback_nltk values(null,1,0,'"+session['uid']+"')")
        else:
            q = "update feedback_nltk set positive_count=positive_count+1 where user_id='"+id+"'"
            ob.update(q)
            # cursor = connection.cursor()
            # cursor.execute(
            #     "update feedback_nltk set positive_count=positive_count+1 where to_user_id='" + to_user_id + "' ")
    else:
        print('The text is negative')
        a = "select * from feedback_nltk where user_id ='" +id+ "'"
        pins = ob.selectOne(a)
        # cursor = connection.cursor()
        # cursor.execute("select * from feedback_nltk where to_user_id='" + to_user_id + "' ")
        # pins = cursor.fetchone()
        if pins == None:
            q = "insert into feedback_nltk values(null,0,1,'" +id+ "')"
            ob.insert(q)
            # cursor = connection.cursor()
            # cursor.execute("insert into feedback_nltk values(null,0,1,'" + to_user_id + "')")
        else:
            q = "update feedback_nltk set negative_count=negative_count+1 where user_id='" +id + "'"
            ob.update(q)
            # cursor = connection.cursor()
            # cursor.execute(
            #     "update feedback_nltk set negative_count=negative_count+1 where to_user_id='" + to_user_id + "' ")
    return redirect(url_for('UserFeedbacks', id=str(id)))


if __name__ == '__main__':
    app.run(debug=True)
