from base64 import b64encode
import logging

from flask import render_template, Blueprint, request
from src.models.user import User
from src.operators.order import get_orders_by_user_id
from src.operators.check import get_check
from src.operators.supplier import get_supplier
from src.operators.doctor import get_all_doctors, get_doctor
from src.operators.recipe import create_recipe, get_recipe, get_recipes_by_user_id
from src.operators.medicine import create_medicine, delete_medicine, get_all_medicines, get_medicine, update_medicine
from src.operators.medicient_substance import create_medicine_substance, get_relation_by_medicine_id
from src.operators.substance import get_all_substances, get_substance
from src.operators.user import create_user, get_user, login_user
from src.schemas.medicine import MedicineSchema
from src.schemas.medicine_substance import MedicineSubstanceSchema
from src.schemas.recipe import RecipeSchema


main = Blueprint("main", __name__)
current_user = User.all()[0]


@main.route('/')
def home(authorization_message=None):
    try:
        data = get_all_medicines().data
    except:
        data = []

    try:
        substances = get_all_substances().data
    except:
        substances = []
        
    logging.warning(current_user)

    return render_template(
        "index.html",
        request=request,
        current_user=current_user,
        authorization_message=authorization_message,
        queryset=data,
        substances=substances
    )


@main.route('/detail/<string:id>')
def detail(id):

    medicine = get_medicine(id).data
    relations = get_relation_by_medicine_id(id).data
    substances = []
    for relation in relations:
        logging.warning(relation)
        substances.append(get_substance(relation["substance_id"]).data)

    return render_template(
        "detail.html",
        current_user=current_user,
        medicine=medicine,
        substances=substances
    )


@main.route("/edit")
def edit_page():
    logging.warning(request.path)
    return render_template(
        "edit.html",
        current_user=current_user,
        url=request.path,
    )

@main.route("/recipes")
def recipes_endpoint(success_uploaded=False):
    logging.warning(current_user.id)
    try:
        recipes = get_recipes_by_user_id(current_user.id).data
    except:
        recipes = []

    data = []
    for recipe in recipes:
        data.append({
            "recipe": recipe,
            "medicine": get_medicine(recipe["medicine_id"]).data,
            "doctor": get_doctor(recipe["doctor_id"]).data
        })

    try:
        doctors = get_all_doctors().data
    except:
        doctors = []

    try:
        medicines = get_all_medicines().data
    except:
        medicines = []

    return render_template(
        "recipes.html",
        current_user=current_user,
        url=request.path,
        data=data,
        doctors=doctors,
        medicines=medicines,
        success_uploaded=success_uploaded
    )


@main.post("/create_recipe")
def create_recipes_endpoint():
    request_form = request.form
    recipe_electronical_signtarure = request_form["inputElectronicSignature"]
    created_on=request_form["inputDate"]
    doctor_id = request_form["selectDoctor"]
    medicine_id = request_form["selectMedicine"]
    
    recipe = RecipeSchema(
        user_id=current_user.id,
        doctor_id=doctor_id,
        medicine_id=medicine_id,
        electronic_signature=recipe_electronical_signtarure,
        created_on=created_on
    )

    create_recipe(recipe)

    return recipes_endpoint(success_uploaded=True)


@main.route("/orders")
def orders_endpoint():
    try:
        orders = get_orders_by_user_id(current_user.id).data
    except:
        orders = []

    data = []
    for order in orders:
        recipe = get_recipe(order.recipe_id).data,
        data.append({
            "order": order,
            "recipe": recipe,
            "supplier": get_supplier(order.medicine_id).data,
            "check": get_check(order.doctor_id).data
        })

    return render_template(
        "orders.html",
        current_user=current_user,
        data=data,
        url=request.path,
    )


@main.get("/edit_medicines")
def medicine_edit_page(
    success=False, 
    success_update=False, 
    seccess_backroll=False, 
    success_delete=False
):
    try:
        medicines = get_all_medicines().data
    except:
        medicines = []

    try:
        substances = get_all_substances().data
    except:
        substances = []

    data = []
    for medicine in medicines:
        relations = get_relation_by_medicine_id(medicine["id"]).data
        substances = []
        for relation in relations:
            substances.append(get_substance(relation["substance_id"]).data)

        data.append({
            "medicine": medicine,
            "substances": substances
        })

    return render_template(
        "edit_medicines.html",
        data=data,
        current_user=current_user,
        substances=substances,
        success=success,
        success_update=success_update,
        seccess_backroll=seccess_backroll,
        success_delete=success_delete,
    )


@main.post("/create_medicine_")
def _create_medicine_endpoint():
    return create_medicine_endpoint(edit=True)


@main.post("/create_medicine")
def create_medicine_endpoint(edit=False):
    request_form = dict(request.form.lists())
    medicine_name = request_form["inputTitle"][0]
    medicine_description = request_form.get("inputDescription", "")[0]
    substance_ids = request_form["selectSubstance"]

    medicine = MedicineSchema(
        name=medicine_name,
        description=medicine_description,
    )
    
    create_medicine(medicine)

    for substance in substance_ids:
        medicine_substance_state = MedicineSubstanceSchema(
            substance_id=substance,
            medicine_id=medicine.id
        )
        create_medicine_substance(medicine_substance_state)
    
    logging.warning(edit)

    if edit:
        return medicine_edit_page(success=True)
    else:
        return home()


@main.get("/update_medicine/<string:id>")
def update_medicine_endpoint(id):
    medicine = get_medicine(id).data
    relations = get_relation_by_medicine_id(medicine.id).data
    substances = []
    for relation in relations:
        substances.append(get_substance(relation["substance_id"]).data)

    data = {
        "medicine": medicine,
        "substances": substances,
    }

    try:
        substances = get_all_substances().data
    except:
        substances = []

    logging.warning(substances)
    logging.warning(data["substances"])

    return render_template(
        "update_medicines.html",
        substances=substances,
        data=data
    )


@main.post("/submit_medicine")
def submit_medicine_update():

    request_form = dict(request.form.lists())

    medicine_id = request_form["MedicineId"][0]
    medicine = get_medicine(medicine_id).data

    medicine_title = request_form["inputTitle"][0]
    medicine_description = request_form["inputDescription"][0]
    substances_ids = request_form["selectSubstance"]

    medicine.name = medicine_title
    medicine.description = medicine_description
    
    substances = []
    for substance_id in substances_ids:
        substances.append(get_substance(substance_id).data)

    update_medicine(medicine, substances)

    return medicine_edit_page(
        success_update=True,
        )
    
@main.get("/delete_medicine/<string:id>")
def delete_medicine_endpoint(id):

    delete_medicine(id)

    return medicine_edit_page(
        success_delete=True,
        )
