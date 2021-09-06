import json
import logging
import os.path
from biomixer_interface.settings import STATIC_PATH
from biomixer_interface.net_functions.ip import IP
from django.views import View
from django.shortcuts import render, redirect
import socket
import qrcode
from django.http import HttpResponse, HttpRequest
from .models import *
from .forms import MaterialFormSet, Labels
from biomixer_interface.arduino.machine_cmd import MachineCmd

machine = MachineCmd()

class HomePage(View):
    """
        Home page view
        manages the request for the home page
    """

    def get(self, request):
        """

        :param request:
        :return:
        """
        return render(request, 'home.html', context={})

    def post(self, request):
        """

        :param request:
        :return:
        """
        pass


class LibraryPage(View):
    """
        Home page view
        manages the request for the home page
    """

    def get(self, request):
        """

        :param request:
        :return:
        """
        recipes = []
        recipes_qry_set = Recipe.objects.all()
        for recipe in recipes_qry_set:
            recipes.append({
                "id": recipe.id,
                "name":  recipe.name,
                "creation_date": str(recipe.creation_date),
                "link": "recipe?name=" + recipe.name
            })
        recipes_json = json.dumps(recipes)
        return render(request, 'library.html', context={"recipes": recipes, "recipes_json": recipes_json})

    def post(self, request):
        """

        :param request:
        :return:
        """
        pass


class MixingPage(View):
    """
        Home page view
        manages the request for the home page
    """

    def get(self, request):
        """

        :param request:
        :return:
        """
        return render(request, 'mixing.html', context={})

    def post(self, request):
        """

        :param request:
        :return:
        """
        pass
        # form = MixForm(request.POST)
        # if form.is_valid():


class PreparingPage(View):
    """
        Home page view
        manages the request for the home page
    """

    if not machine.portIsUsable():
        print("[WARNING]: PLEASE CONNECT ARDUINO TO THE RASPBERRY")

    def get(self, request):
        """
        :param request:
        :return:
        """
        formset = MaterialFormSet()
        return render(request, 'preparing.html', context={'form_pack': zip(formset, Labels.options),
                                                          'formset': formset})

    def post(self, request):
        """
        :param request:
        :return:
        """
        formset = MaterialFormSet(request.POST)
        material_list = []
        material_index = []
        value_list = []

        if formset.is_valid():
            n_recipes = Recipe.objects.all().count()+1
            recipe = Recipe.objects.create(name="New_recipe "+str(n_recipes), tag="", img_link="")
            i = 0
            for answer in formset.cleaned_data:
                Supply.objects.create(recipe=recipe, position=i, material=answer['material'],
                                      value=answer['value'], type=answer['type'])
                material_list.append(answer['material'].name)
                value_list.append(answer['value'])
                material_index.append(i+1)
                i += 1
            # new_request = HttpRequest()
            # query  = QuerDict(f'water={value_list[0]}')
            # new_request.path = url('back_end:machine_controller')
            # new_request.GET = query
            # render(request)

            machine.set_values(cmd=machine.CMD_SET_VALUES,
                        d1=value_list[0], d2=value_list[1],
                        d3=value_list[2], d4=value_list[3],
                        d5=value_list[4])
            machine.write()

        else:
            print(formset.errors)

        return render(request, 'mixing.html', context={'materials_and_index': zip(material_list, material_index),
                                                       'materials': material_list,
                                                       'values': value_list})


class QRConnect(View):
    already_visited = True

    def get(self, request):
        if self.already_visited:
            path = os.path.join(STATIC_PATH, 'img')
            print(path)
            host = IP.get_ip()
            ip = socket.gethostbyname(host)
            ip = 'http://' + ip + ':8000'
            img = qrcode.make(ip)
            img.save(path + '/qrip.png', )
            print(img)

        return render(request, 'qrip.html')


class DropZone(View):
    def get(self, request):
        return render(request, 'dzone.html')

    def post(self, request):
        my_file = request.FILES.get('file')
        Doc.objects.create(upload=my_file)
        return HttpResponse('upload')

    @staticmethod
    def success(request):
        return render(request, 'dzone_success.html')


class LiveOutputs(View):
    def txt(self):
        new_text = machine.read(size=10).decode()
        print(new_text)
        path = os.path.join(STATIC_PATH, 'machine_output/')
        file = open(path + 'output.txt', 'a')
        file.write("\n")
        file.write(str(new_text))
        file.close()

        file = open(path + 'output.txt', 'r')
        text = file.read()
        response = HttpResponse()
        response.write("<pre>" + text + "</pre>")
        return response


class RecipePage(View):
    def get(self, request):
        name = request.GET.get("name")
        recipe = Recipe.objects.get(name=name)
        supply_qry_set = Supply.objects.filter(recipe=recipe).order_by('position')
        steps_qry_set = Step.objects.filter(recipe_id=recipe)
        supplies = []
        materials = []
        values = []
        for supply in supply_qry_set:
            material = supply.material.name
            materials.append(material)
            values.append(supply.value)
            supplies.append({
                "position": supply.position+1,
                "material": material,
                "value": supply.value,
                "type": supply.type,
            })
        print(recipe, supplies)
        return render(request, template_name="recipe.html", context={"materials": materials,
                                                                     "values": values,
                                                                     "supplies": supplies,
                                                                     "recipe_name": recipe.name,
                                                                     "creation_date": recipe.creation_date})

    def post(self, request):
        pass


class MachineController(View):

    @staticmethod
    def check_values(value_list):
        for i in range(len(value_list)):
            if  value_list[i] is None:
                value_list[i] = 0
        return value_list

    def get(self, request):

        cmd = request.GET.get("cmd")
        water = request.GET.get("water")
        agar = request.GET.get("agar")
        propinate = request.GET.get("propinate")
        glycerin = request.GET.get("glycerin")
        residue = request.GET.get("residue")
        value_list = [water, agar, propinate, glycerin, residue]
        value_list = self.check_values(value_list)
        message = "Get " + str(value_list)
        if cmd is not None:
            print(f"CMD= {cmd}")
        # write
        #machine.write(value_list)

        return HttpResponse(content=message)

    def post(self, request):
        return HttpResponse(content='POST')
