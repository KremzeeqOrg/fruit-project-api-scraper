

fruity_vice_ssm_value_dict = {
                              "source_api": "fruity-vice",
                              "auth_header": {},
                              "custom_field_info" : {},
                              "source_api_endpoint": "https://www.fruityvice.com/api/fruit/all",
                              "source_api_records_key": "",
                              "field_mapping": {
                                                "id" : "id1",
                                                "name" : "name",
                                                "family" : "family1",
                                                "genus" : "genus1",
                                                "order" : "order1"
                              },
                              "dynamo_db_config" : { "table" : "fruit", "hash_key": "name"}

                            }

the_cocktail_db_ssm_value_dict = {
    "source_api": "the-cocktail-db",
    "auth_header": {},
    "source_api_endpoint": "https://www.thecocktaildb.com/api/json/v1/1/search.php",
    "source_api_records_key": "drinks",
"custom_field_info" : {"ingredient_max_count" : 15},
    "field_mapping": {
        "idDrink": "id",
        "strDrink": "name",
        "strAlcoholic": "alcoholic",
        "strGlass": "glass",
        "strInstructions": "instructions",
        "strDrinkThumb": "thumbnail_link",
        "strIngredient1": "ingredient_1",
        "strIngredient2": "ingredient_2",
        "strIngredient3": "ingredient_3",
        "strIngredient4": "ingredient_4",
        "strIngredient5": "ingredient_5",
        "strIngredient6": "ingredient_6",
        "strIngredient7": "ingredient_7",
        "strIngredient8": "ingredient_8",
        "strIngredient9": "ingredient_9",
        "strIngredient10": "ingredient_10",
        "strIngredient11": "ingredient_11",
        "strIngredient12": "ingredient_12",
        "strIngredient13": "ingredient_13",
        "strIngredient14": "ingredient_14",
        "strIngredient15": "ingredient_15",
        "strMeasure1": "measure_1",
        "strMeasure2": "measure_2",
        "strMeasure3": "measure_3",
        "strMeasure4": "measure_4",
        "strMeasure5": "measure_5",
        "strMeasure6": "measure_6",
        "strMeasure7": "measure_7",
        "strMeasure8": "measure_8",
        "strMeasure9": "measure_9",
        "strMeasure10": "measure_10",
        "strMeasure11": "measure_11",
        "strMeasure12": "measure_12",
        "strMeasure13": "measure_13",
        "strMeasure14": "measure_14",
        "strMeasure15": "measure_15",
        "strImageSource": "image_source",
        "strImageAttribution": "image_attribution",
        "strCreativeCommonsConfirmed": "creative_commons_confirmed"
    },
    "dynamo_db_config": {
        "table": "cocktail-recipes",
        "hash_key": "name"
    }
}

sample_ssm_value_dicts = { "fruity-vice" : fruity_vice_ssm_value_dict,
                          "the-cocktail-db" : the_cocktail_db_ssm_value_dict
                        }