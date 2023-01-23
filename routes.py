"""Routes."""

from operator import itemgetter

from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request

from app import phone, factory

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
    if request.method == "POST":
        # delete phone
        if request.form.get("delete"):
            phone.delete_one({"_id": ObjectId(request.form.get("delete"))})

        # assign one-to-many relationship (factory to phone)
        elif request.form.get("assign"):
            _id = {"_id": ObjectId(request.form.get("assign"))}
            factory_1 = factory.find({}).limit(1)
            phone.update_one(
                _id, {"$set": {"factory_id": ObjectId(factory_1[0]["_id"])}}
            )

    models = list(
        phone.find({"brand": brand}, projection={"model": True, "factory_id": True})
    )
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
        # update model name
        if request.form.get("model"):
            phone.update_one(_id, {"$set": {"model": request.form["model"]}})
        # increase/decrease year
        if request.form.get("year"):
            phone.update_one(_id, {"$inc": {"year": int(request.form["year"])}})
        # add new item to array
        if request.form.get("new_misc"):
            phone.update_one(_id, {"$addToSet": {"misc": request.form["new_misc"]}})

    phone_data = phone.find_one(_id)

    return render_template("model.html", phone_data=phone_data)


@main.route("/filter", methods=["GET", "POST"])
def get_filtered_results():
    """Filter the result list by various parameters."""
    # get min and max years within all items in DB
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
            # filter by year with slider
            case "slider":
                filtered_data = phone.find(
                    {"year": {"$lte": int(request.form["yearRangeSlider"])}}
                ).sort("brand")
            # filter by year within min and max years
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
