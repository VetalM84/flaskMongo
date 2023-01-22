"""Routes."""

from operator import itemgetter

from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, redirect

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
    #     }
    # )
    brands = list(
        phone.find(projection={"brand": True, "_id": False}).distinct("brand")
    )
    return render_template("index.html", context=brands)


@main.route("/models/<string:brand>", methods=["GET", "POST"])
def get_models(brand: str):
    """A page with a list of models to appropriate brand."""
    if request.method == "POST" and request.form.get("delete"):
        phone.delete_one({"_id": ObjectId(request.form.get("delete"))})

    models = list(phone.find({"brand": brand}, projection={"model": True}))
    cnt = phone.count_documents({"brand": brand})
    models_list = sorted(models, key=itemgetter("model"), reverse=True)

    context = {
        "models": models_list,
        "brand": brand,
        "cnt": cnt,
    }
    return render_template("models.html", context=context)


@main.route("/<string:phone_id>", methods=["GET", "POST"])
def get_single_model(phone_id):
    """Get single phone model. Change some parameters on POST."""
    _id = {"_id": ObjectId(phone_id)}
    if request.method == "POST":
        if request.form.get("model"):
            phone.update_one(_id, {"$set": {"model": request.form["model"]}})
        if request.form.get("year"):
            phone.update_one(_id, {"$inc": {"year": int(request.form["year"])}})

    phone_data = phone.find_one(_id)

    print(type(phone_data), "type_phone_data")
    print(phone_data, "phone_data")
    return render_template("model.html", phone_data=phone_data)


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
        match request.form.get("filterType"):
            case "slider":
                filtered_data = phone.find(
                    {"year": {"$lte": int(request.form["yearRangeSlider"])}}
                ).sort("brand")
            case "range":
                filtered_data = phone.find(
                    {
                        "$and": [
                            {"year": {"$gte": int(request.form["yearStart"])}},
                            {"year": {"$lte": int(request.form["yearEnd"])}},
                        ]
                    }
                ).sort("brand")
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
