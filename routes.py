"""Routes."""

from flask import Blueprint, render_template
from models import Phone, CPU
from bson.json_util import dumps, loads


main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Main page with list of brands."""
    # phone.insert_one(
    #     {
    #         "brand": "Samsung",
    #         "model": "Galaxy S14",
    #         "year": 2022,
    #         "CPU": {
    #             "manufacturer": "Snapdragon 895",
    #             "cores": 16,
    #         },
    #         "RAM": {
    #             "volume": 16,
    #             "meter": "Gb",
    #             "type": "DRR4",
    #         },
    #         "display": 7,
    #         "wireless": {
    #             "Bluetooth": 6.0,
    #             "WIFI": {
    #                 "type": "Dual band",
    #                 "2.5 GHz": True,
    #                 "5 GHz": True,
    #             },
    #             "GPS": True,
    #         },
    #         "OS": {
    #             "name": "Android",
    #             "version": 13,
    #         },
    #
    #     }
    # )
    # p = Phone(
    #     brand="Apple", model="iPhone XR", year=2022, display=7
    # )
    # p.cpu = CPU(manufacturer="Snapdragon 895", cores=8)
    # p.save()
    brands = Phone.objects.only("brand")
    return render_template("index.html", context=brands)


@main.route("/models/<brand>")
def get_models(brand: str):
    """."""
    context = {
        "models": Phone.objects(brand=brand).only("model"),
        "brand": brand,
    }
    return render_template("models.html", context=context)


@main.route("/<brand>/<model>")
def get_single_model(brand: str, model: str):
    """."""
    phone = Phone.objects(brand=brand, model=model).first()
    context = {
        "model_data": list(phone),
        "model": model,
        "brand": brand,
    }
    print(phone.to_mongo())
    return render_template("model.html", phone_data=phone.to_mongo())
