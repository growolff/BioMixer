import json
import logging
import os.path
from biomixer_interface.settings import STATIC_PATH
from biomixer_interface.net_functions.ip import IP
from django.views import View
from django.shortcuts import render, redirect
import socket
import qrcode
from django.http import HttpResponse
from .models import *
from .forms import MaterialFormSet, Labels



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
            # # BEGIN ARDUINO
            # arduino = serial.Serial('/dev/ttyACM0',9600,timeout=10)
            # # SEND Values
            # machine = MachineCmd()
            # machine.set_values(d1=value_list[0], d2=value_list[1],
            #                    d3=value_list[2], d4=value_list[3],
            #                    d5=value_list[4])
            # machine.serialize()
            # print(machine.to_hex())
            # if arduino.write(machine.packet):
            #     print('OK')
            #     try:
            #         packet = arduino.read(1)
            #         print("original packet: ", packet.hex())
            #     except serial.SerialException as e:
            #         print(e)
            #
            # else:
            #     print('fail')
            #
            # # arduino.close()
            # END ARDUINO
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
        path = os.path.join(STATIC_PATH, 'machine_output/')
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
