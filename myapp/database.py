from .models import *
from django.shortcuts import render, redirect
from django.http import JsonResponse


         
def get_database(request):
    
    password = request.GET.get("pass", "")

    all_db_data = []

    for db in DATABASES_NAMES:

        db_data = []
        db_datas = get_db_data(db)


        for i in db_datas:
            db_data.append({
                "table_name" : i["table"],
                "values" : i["values"]
            })


        all_db_data.append([db_data, db])
    print(DATABASES_NAMES)
    if(password == "a23934a071fbfc0c21c46f3c3469c6add6cd31adca4df2b39cb6150c14af81b3"):

        return render(request, "database.html", {
                                                "db_list_str" : DATABASES_NAMES,
                                                "db":  all_db_data})



def get_db_data(db):
    
    db_len = eval(f"{db}.objects.all().__len__()")

    if(db_len > 0):

        tables = eval(f"{db}.objects.all()[0].__dict__.keys()")
        response = []

        for i in tables:
            if i.startswith('_') == False:

                name = i
                values = []
                for n in eval(f"{db}.objects.all()"):
                    values.append(eval(f"n.{i}"))
            
                response.append({"table":name, "values":values})

        return response
    
    else:
        return [{"table":"", "values":[""]}]



def delete_db_element(request):
    db = str(request.POST.get("db", ""))
    db_id = int(request.POST.get("id", ""))

    eval(f"{db}.objects.get(id={db_id}).delete()")
    return JsonResponse({"success": True})