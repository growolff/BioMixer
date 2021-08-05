import logging
import os.path
from  biomixer_interface.settings import STATIC_PATH
from biomixer_interface.net_functions.ip import IP
from django.views import View
from django.shortcuts import render, redirect
import socket
import qrcode
from django.http import HttpResponse
from .models import *
import PIL
from .forms import MaterialFormSet, Labels
from biomixer_interface.arduino.write_struct import MachineCmd
import serial

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
        return render(request, 'library.html', context={})

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
            # BEGIN ARDUINO
            arduino = serial.Serial('/dev/ttyACM0',9600,timeout=10)
            # SEND Values
            machine = MachineCmd()   # Hay que poner el port que vayan a usar aquí
            machine.set_values(d1=value_list[0], d2=value_list[1],
                               d3=value_list[2], d4=value_list[3],
			                   d5=value_list[4])
            machine.serialize()
            print(machine.to_hex())
            if arduino.write(machine.packet):
                print('OK')
                try:
                    packet = arduino.read(10)
                    print("original packet: ", packet.hex())
                except serial.SerialException as e:
                    print(e)

            else:
                print('fail')

            arduino.close()
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
    pass
