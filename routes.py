"""Routes."""

from operator import itemgetter

from flask import Blueprint, render_template, request
from bson.json_util import dumps, loads
from app import phone

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Main page with a list of brands."""
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
    brands = list(
        phone.find(projection={"brand": True, "_id": False}).distinct("brand")
    )
    # print(json_util.dumps(brands))
    print(brands)
    print(type(brands))
    return render_template("index.html", context=brands)


@main.route("/models/<string:brand>")
def get_models(brand: str):
    """A page with a list of models to appropriate brand."""
    models = list(
        phone.find({"brand": brand}, projection={"model": True, "_id": False})
    )
    cnt = phone.count_documents({"brand": brand})
    models_list = sorted(models, key=itemgetter("model"), reverse=True)
    context = {
        "models": models_list,
        "brand": brand,
        "cnt": cnt,
    }
    return render_template("models.html", context=context)


@main.route("/<string:brand>/<string:model>")
def get_single_model(brand: str, model: str):
    """."""
    phone_data = phone.find_one({"brand": brand, "model": model})
    # phone.update(ram={"volume": 16, "meter": "Gb", "type": "DRR4"})
    # w = Wireless(bluetooth=6.0, gps=True, wifi={"exist": "Dual band", "ghz_24": True, "ghz_5": False})
    # w = {"wifi": {"exist": "Dual band", "ghz_24": True, "ghz_5": False}}
    # phone.update(wireless=w)
    print(type(phone), "phone")
    print(type(phone_data), "phone_data")
    return render_template(
        "model.html", phone_data=phone_data, model=model, brand=brand
    )


@main.route("/filter", methods=["GET", "POST"])
def get_filtered_results():
    """."""
    year = list(
        phone.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "max_val": {"$max": "$year"},
                        "min_val": {"$min": "$year"},
                    }
                }
            ]
        )
    )
    filtered_data = []

    if request.method == "POST":
        filtered_data = phone.find(
            {"year": {"$not": {"$gt": int(request.form["yearRange"])}}}
        )
    return render_template("filter.html", year=year, filtered_data=filtered_data)


@main.route("/search", methods=["GET", "POST"])
def search():
    """Search by brand or model."""
    search_result = []
    if request.method == "POST":
        search_request = request.form["search"]
        search_result = phone.find(
            {"$or": [{"brand": search_request}, {"model": search_request}]}
        )
    return render_template("search.html", context=search_result)
