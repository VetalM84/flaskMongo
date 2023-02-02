"""Routes."""
from datetime import datetime
from operator import itemgetter

from bson.objectid import ObjectId
from flask import Blueprint, render_template, request

from app import client, factory, phone, transaction

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Main page with a list of brands."""
    # phone.insert_many([
    #     {
    #         "brand": "Samsung",
    #         "model": "Galaxy S18",
    #         "year": 2020,
    #         "image": "https://smartphonemodel.com/wp-content/uploads/2020/01/Samsung-Galaxy-S18.jpg",
    #         "CPU": {
    #             "manufacturer": "Snapdragon 725",
    #             "cores": 8,
    #         },
    #         "misc": ["GPS", "Wifi"]
    #     },
    #     {
    #         "brand": "Apple",
    #         "model": "iPhone XR",
    #         "year": 2016,
    #         "image": "https://apple-mania.com.ua/media/catalog/product/cache/e026f651b05122a6916299262b60c47d/a/p/apple-iphone-xr-yellow_1.png",
    #         "CPU": {
    #             "manufacturer": "A12 Bionic",
    #             "cores": 10,
    #         },
    #         "misc": ["Bluetooth 5.0", "NFC"]
    #     },
    #     {
    #         "brand": "Apple",
    #         "model": "iPhone SE",
    #         "year": 2010,
    #         "image": "https://www.ixbt.com/img/n1/news/2021/3/3/Ez9zhLUXsAEbBcq_large.jpg",
    #         "CPU": {
    #             "manufacturer": "A8",
    #             "cores": 4,
    #         },
    #     },
    #     {
    #         "brand": "Motorola",
    #         "model": "Moto E",
    #         "year": 2012,
    #         "image": "https://i.citrus.world/imgcache/size_800/uploads/shop/a/1/a1335892123d3204f27798192ba7e7d3.jpg",
    #         "CPU": {
    #             "manufacturer": "Mediatek 200",
    #             "cores": 4,
    #         },
    #         "misc": ["GPS", "Wifi"]
    #     },
    #
    # ])

    # factory.insert_many([
    #     {
    #         "name": "Foxconn",
    #         "stock": 1000,
    #     },
    #     {
    #         "name": "Samsung",
    #         "stock": 2000,
    #     },
    #     {
    #         "name": "Biostar",
    #         "stock": 99,
    #     },
    # ])
    brands = list(
        phone.find({}, projection={"brand": True, "_id": False}).distinct("brand")
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
        elif request.form.get("phone_id") and request.form.get("factory_id"):
            _id = {"_id": ObjectId(request.form.get("phone_id"))}
            factory_id = ObjectId(request.form.get("factory_id"))
            phone.update_one(_id, {"$set": {"factory_id": factory_id}})

    models = phone.aggregate(
        [
            {"$match": {"brand": brand}},
            {
                "$lookup": {
                    "from": "factory",
                    "localField": "factory_id",
                    "foreignField": "_id",
                    "as": "factories",
                }
            },
            {
                "$project": {
                    "model": True,
                    "image": True,
                    "factory": {"$arrayElemAt": ["$factories", 0]},
                }
            },
        ]
    )
    cnt = phone.count_documents({"brand": brand})
    models_list = sorted(models, key=itemgetter("model"), reverse=True)
    factories = list(factory.find({}))
    context = {
        "factories": factories,
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
    """Case intensive search by brand or model."""
    search_result = []
    if request.method == "POST":
        search_request = request.form["search"]
        search_result = phone.find(
            {
                "$or": [
                    {"brand": {"$regex": search_request, "$options": "-i"}},
                    {"model": {"$regex": search_request, "$options": "-i"}},
                ]
            }
        )
    return render_template("search.html", context=search_result)


@main.route("/aggregate")
def aggregation():
    """Aggregation example."""
    result = list(
        factory.aggregate(
            [
                {
                    "$lookup": {
                        "from": "phone",
                        "localField": "_id",
                        "foreignField": "factory_id",
                        "as": "phones",
                    }
                },
                {"$addFields": {"total": {"$size": "$phones"}}},
                {"$project": {"stock": 0, "_id": 0, "phones": {"_id": 0}}},
            ]
        )
    )
    # result = phone.aggregate(
    #     [
    #         {"$match": {}},
    #         {
    #             "$group": {
    #                 "_id": "$brand",
    #                 "cnt": {
    #                     "$sum": {
    #                         "$cond": [{"$eq": [{"$type": "$model"}, "string"]}, 1, 0]
    #                     }
    #                 },
    #             }
    #         },
    #     ]
    # )
    print(list(result))
    return render_template("aggregate.html", context=result)


@main.route("/transaction", methods=["GET", "POST"])
def make_transaction():
    """Make a transaction. Transfer certain amount from one factory to another."""
    if request.method == "POST":

        def callback(db_session):
            """Transaction wrapper."""
            factories_collection = db_session.client["Comparison"]["factory"]
            transactions_collection = db_session.client["Comparison"]["transaction"]
            from_factory_id = request.form.get("from_factory_id")
            to_factory_id = request.form.get("to_factory_id")
            amount = int(request.form.get("amount"))

            new_transaction = {
                "from_factory_id": ObjectId(from_factory_id),
                "to_factory_id": ObjectId(to_factory_id),
                "amount": amount,
                "date": datetime.utcnow(),
            }
            factories_collection.update_one(
                {"_id": ObjectId(from_factory_id)},
                {"$inc": {"stock": -amount}},
                session=db_session,
            )
            factories_collection.update_one(
                {"_id": ObjectId(to_factory_id)},
                {"$inc": {"stock": amount}},
                session=db_session,
            )
            transactions_collection.insert_one(new_transaction, session=db_session)

        # start transaction
        with client.start_session() as session:
            session.with_transaction(callback)

    factories = list(factory.find({}))
    transactions = list(
        transaction.aggregate(
            [
                {
                    "$lookup": {
                        "from": "factory",
                        "localField": "from_factory_id",
                        "foreignField": "_id",
                        "as": "from_factory",
                    }
                },
                {
                    "$lookup": {
                        "from": "factory",
                        "localField": "to_factory_id",
                        "foreignField": "_id",
                        "as": "to_factory",
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "amount": 1,
                        "date": 1,
                        "from_factory": {"name": 1},
                        "to_factory": {"name": 1},
                    }
                },
            ]
        )
    )
    return render_template(
        "transaction.html",
        context={"factories": factories, "transactions": transactions},
    )
