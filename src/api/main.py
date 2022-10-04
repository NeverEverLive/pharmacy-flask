import datetime
import uuid
import logging

from flask import render_template, Blueprint, request
from sqlalchemy import select, func

from src.models.user import User
from src.models.order import Order
from src.models.role import Role
from src.models.base_model import get_session
from src.operators.order import get_orders_by_user_id, create_order
from src.operators.check import get_check, create_check
from src.operators.role import get_role, get_all_roles, create_role, update_role, delete_role
from src.operators.user import get_user, get_all_users, create_user, update_user, delete_user, login
from src.operators.supplier import get_supplier, create_supplier, get_all_suppliers, update_supplier, delete_supplier
from src.operators.doctor import get_all_doctors, get_doctor, create_doctor, update_doctor, delete_doctor
from src.operators.recipe import create_recipe, get_recipe, get_recipes_by_user_id, get_recipes_by_user_and_medicine_id
from src.operators.medicine import create_medicine, delete_medicine, get_all_medicines, get_medicine, update_medicine
from src.operators.medicient_substance import create_medicine_substance, get_relation_by_medicine_id
from src.operators.substance import get_all_substances, get_substance, create_substance, update_substance, delete_substance
from src.schemas.medicine import MedicineSchema
from src.schemas.medicine_substance import MedicineSubstanceSchema
from src.schemas.recipe import RecipeSchema
from src.schemas.substance import SubstanceSchema
from src.schemas.doctor import DoctorSchema
from src.schemas.supplier import SupplierSchema
from src.schemas.role import RoleSchema
from src.schemas.user import UserSchema, LoginUserSchema
from src.schemas.check import CheckSchema
from src.schemas.order import OrderSchema


main = Blueprint("main", __name__)
current_user = User.all()[0]
cart = []


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
    logging.warning(cart)

    return render_template(
        "index.html",
        request=request,
        current_user=current_user,
        authorization_message=authorization_message,
        queryset=data,
        substances=substances,
        cart=cart
    )


@main.route('/cart')
def cart_endpoint(success=None):
    return render_template(
        "cart.html",
        medicines=cart,
        current_user=current_user
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
    recipe_electronic_signature = request_form["inputElectronicSignature"]
    created_on = request_form["inputDate"]
    doctor_id = request_form["selectDoctor"]
    medicine_id = request_form["selectMedicine"]

    recipe = RecipeSchema(
        user_id=current_user.id,
        doctor_id=doctor_id,
        medicine_id=medicine_id,
        electronic_signature=recipe_electronic_signature,
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
        success_backroll=False,
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

    logging.warning("hahahah")
    logging.warning(substances)

    data = []
    for medicine in medicines:
        relations = get_relation_by_medicine_id(medicine["id"]).data
        relation_substances = []
        for relation in relations:
            relation_substances.append(get_substance(relation["substance_id"]).data)

        data.append({
            "medicine": medicine,
            "substances": relation_substances
        })

    return render_template(
        "edit_medicines.html",
        data=data,
        current_user=current_user,
        substances=substances,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
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


@main.get("/edit_substance")
def substance_edit_page(
        success=False,
        success_update=False,
        success_backroll=False,
        success_delete=False
):
    try:
        substances = get_all_substances().data
    except:
        substances = []

    return render_template(
        "edit_substance.html",
        current_user=current_user,
        substances=substances,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
        success_delete=success_delete,
    )


@main.post("/create_substance")
def create_substance_endpoint():
    request_form = dict(request.form.lists())
    substance_name = request_form["inputTitle"][0]

    substance = SubstanceSchema(name=substance_name)

    create_substance(substance)

    return substance_edit_page(success=True)


@main.get("/update_substance/<string:id>")
def update_substance_endpoint(id):
    substance = get_substance(id).data

    return render_template(
        "update_substance.html",
        substance=substance,
    )


@main.post("/submit_substance")
def submit_substance_update():
    request_form = request.form

    substance_id = request_form["substanceId"]
    substance_title = request_form["inputTitle"]
    substance = SubstanceSchema(
        id=uuid.UUID(substance_id),
        name=substance_title
    )

    update_substance(substance)

    return substance_edit_page(
        success_update=True,
    )


@main.get("/delete_substance/<string:id>")
def delete_substance_endpoint(id):
    delete_substance(id)
    return substance_edit_page(
        success_delete=True,
    )


@main.get("/edit_doctor")
def doctor_edit_page(
        success=False,
        success_update=False,
        success_backroll=False,
        success_delete=False
):
    try:
        doctors = get_all_doctors().data
    except:
        doctors = []

    return render_template(
        "edit_doctor.html",
        current_user=current_user,
        doctors=doctors,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
        success_delete=success_delete,
    )


@main.post("/create_doctor")
def create_doctor_endpoint():
    request_form = request.form
    doctor_first_name, doctor_last_name = request_form["inputTitle"].strip().split()
    doctor_hospital = request_form["inputHospital"]

    doctor = DoctorSchema(
        first_name=doctor_first_name,
        last_name=doctor_last_name,
        hospital=doctor_hospital,
    )

    create_doctor(doctor)

    return doctor_edit_page(success=True)


@main.get("/update_doctor/<string:id>")
def update_doctor_endpoint(id):
    doctor = get_doctor(id).data

    return render_template(
        "update_doctor.html",
        doctor=doctor,
    )


@main.post("/submit_doctor")
def submit_doctor_update():
    request_form = request.form

    doctor_id = request_form["doctorId"]
    doctor_first_name = request_form["inputFirstName"]
    doctor_last_name = request_form["inputLastName"]
    doctor_hospital = request_form["inputHospital"]
    doctor = DoctorSchema(
        id=uuid.UUID(doctor_id),
        first_name=doctor_first_name,
        last_name=doctor_last_name,
        hospital=doctor_hospital,
    )

    update_doctor(doctor)

    return doctor_edit_page(
        success_update=True,
    )


@main.get("/delete_doctor/<string:id>")
def delete_doctor_endpoint(id):
    delete_doctor(id)
    return doctor_edit_page(
        success_delete=True,
    )


@main.get("/edit_supplier")
def supplier_edit_page(
        success=False,
        success_update=False,
        success_backroll=False,
        success_delete=False
):
    try:
        suppliers = get_all_suppliers().data
    except:
        suppliers = []

    return render_template(
        "edit_supplier.html",
        current_user=current_user,
        suppliers=suppliers,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
        success_delete=success_delete,
    )


@main.post("/create_supplier")
def create_supplier_endpoint():
    request_form = request.form
    supplier_first_name, supplier_last_name = request_form["inputTitle"].strip().split()
    supplier_company = request_form["inputCompany"]

    supplier = SupplierSchema(
        first_name=supplier_first_name,
        last_name=supplier_last_name,
        company=supplier_company,
    )

    create_supplier(supplier)

    return supplier_edit_page(success=True)


@main.get("/update_supplier/<string:id>")
def update_supplier_endpoint(id):
    supplier = get_supplier(id).data

    return render_template(
        "update_supplier.html",
        supplier=supplier,
    )


@main.post("/submit_supplier")
def submit_supplier_update():
    request_form = request.form

    supplier_id = request_form["supplierId"]
    supplier_first_name = request_form["inputFirstName"]
    supplier_last_name = request_form["inputLastName"]
    supplier_company = request_form["inputCompany"]
    supplier = SupplierSchema(
        id=uuid.UUID(supplier_id),
        first_name=supplier_first_name,
        last_name=supplier_last_name,
        company=supplier_company,
    )

    update_supplier(supplier)

    return supplier_edit_page(
        success_update=True,
    )


@main.get("/delete_supplier/<string:id>")
def delete_supplier_endpoint(id):
    delete_supplier(id)
    return supplier_edit_page(
        success_delete=True,
    )


@main.get("/edit_role")
def role_edit_page(
        success=False,
        success_update=False,
        success_backroll=False,
        success_delete=False
):
    try:
        roles = get_all_roles().data
    except:
        roles = []

    return render_template(
        "edit_role.html",
        current_user=current_user,
        roles=roles,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
        success_delete=success_delete,
    )


@main.post("/create_role")
def create_role_endpoint():
    request_form = request.form
    role_name = request_form["inputName"]

    role = RoleSchema(
        name=role_name,
    )

    create_role(role)

    return role_edit_page(success=True)


@main.get("/update_role/<string:id>")
def update_role_endpoint(id):
    role = get_role(id).data

    return render_template(
        "update_role.html",
        role=role,
    )


@main.post("/submit_role")
def submit_role_update():
    request_form = request.form

    role_id = request_form["roleId"]
    role_name = request_form["inputName"]
    role = RoleSchema(
        id=uuid.UUID(role_id),
        name=role_name,
    )

    update_role(role)

    return role_edit_page(
        success_update=True,
    )


@main.get("/delete_role/<string:id>")
def delete_role_endpoint(id):
    delete_role(id)
    return role_edit_page(
        success_delete=True,
    )


@main.get("/edit_user")
def user_edit_page(
        success=False,
        success_update=False,
        success_backroll=False,
        success_delete=False
):
    try:
        users = get_all_users().data
    except:
        users = []

    try:
        roles = get_all_roles().data
    except:
        roles = []

    return render_template(
        "edit_user.html",
        current_user=current_user,
        users=users,
        roles=roles,
        success=success,
        success_update=success_update,
        success_backroll=success_backroll,
        success_delete=success_delete,
    )


@main.post("/create_user")
def create_user_endpoint():
    request_form = request.form
    user_username = request_form["inputUserName"]
    user_password = request_form["inputPassword"]
    user_role = request_form["selectRole"]

    user = UserSchema(
        username=user_username,
        hash_password=user_password,
        role_id=user_role,
    )

    create_user(user)

    return user_edit_page(success=True)


@main.get("/update_user/<string:id>")
def update_user_endpoint(id):
    user = get_user(id).data
    current_role = get_role(user["role_id"]).data
    roles = get_all_roles().data

    logging.warning(current_role)

    return render_template(
        "update_user.html",
        user=user,
        current_role=current_role,
        roles=roles
    )


@main.post("/submit_user")
def submit_user_update():
    request_form = request.form

    user_id = request_form["userId"]
    user_username = request_form["inputUserName"]
    user_password = request_form["inputPassword"]
    user_role = request_form["selectRole"]

    logging.warning("asdasdasd")
    logging.warning(user_role)

    user = UserSchema(
        id=user_id,
        username=user_username,
        hash_password=user_password,
        role_id=user_role,
    )

    update_user(user)

    return user_edit_page(
        success_update=True,
    )


@main.get("/delete_user/<string:id>")
def delete_user_endpoint(id):
    delete_user(id)
    return user_edit_page(
        success_delete=True,
    )


@main.get("/add_cart_medicine/<string:id>")
def add_medicine_to_cart(id: MedicineSchema):
    logging.warning(1)
    # id, template = id.strip().split()
    medicine = get_medicine(id).data
    cart.append(medicine)
    logging.warning(cart)
    return home()
    # if template:
    #     return home()
    # else:
    #     return cart_endpoint()


@main.get("/delete_cart_medicine/<string:id>")
def delete_medicine_to_cart(id: MedicineSchema):
    id, template = id.strip().split()
    medicine = get_medicine(id).data
    cart.remove(medicine)
    logging.warning(template)
    logging.warning(bool(template))
    if int(template):
        return home()
    else:
        return cart_endpoint()


@main.get("create_order")
def create_order_endpoint():
    recipe_ids = []
    total_price = 0
    for item in cart:
        total_price += item.price
        recipe = get_recipes_by_user_and_medicine_id(current_user.id, item.id)
        recipe_ids.append(recipe)

    check = CheckSchema(
        date=datetime.date.today(),
        total_price=total_price
    )
    check = create_check(check).data

    with get_session() as session:
        order_count = session.execute(select(
            func.count()
        ).select_from(
            Order
        )).scalar()

    order = OrderSchema(
        recipe_id=recipe_ids,
        supplier_id=supplier_id,
        check_id=check.id,
        user_id=current_user.id,
        name=f"Order number {order_count}"
    )
    create_order(order)


@main.get("/login")
def get_login_request_edpoint(error_message=None):
    return render_template(
        "login.html",
        current_user=current_user,
        error_message=error_message
    )


@main.post("/user/login")
def login_user_edpoint():
    request_form = request.form

    data = {
        "username": request_form["inputUsername"],
        "password": request_form["inputPassword"]
    }

    global current_user
    try:
        current_user = login(LoginUserSchema.parse_obj(data)).data
    except ValueError as error:
        return get_login_request_edpoint(str(error))

    logging.warning(current_user)

    return home(authorization_message="You've successfully logged in")


@main.get("/user/logout")
def logout_user_edpoint():
    global current_user

    current_user = None

    return home(authorization_message="You successfully logged out")


@main.get("/register")
def get_signin_request_edpoint():
    logging.warning("1")

    return render_template(
        "register.html",
        current_user=current_user,
    )


@main.post("/user/register")
def register_user_edpoint():
    request_form = request.form

    with get_session() as session:
        user_role = session.execute(select(
            Role.id
        ).where(
            Role.name == "user"
        )).scalar()

    data = {
        "username": request_form["inputUsername"],
        "password": request_form["inputPassword"],
        "role_id": user_role
    }

    global current_user

    current_user = create_user(UserSchema.parse_obj(data)).data

    logging.warning(current_user)

    return home(authorization_message="Your account seccessfuly created")
