# -*- coding: utf-8 -*-

from decimal import Decimal

def extenso(valor, MoedaPlural, MoedaSingular):

    Buf = ""

    Negativo = (valor < 0)
    valor = abs(Decimal(valor))

    extenso = ""

    if valor:
        Unidades = ["", "Um", "Dois", "Três", "Quatro", "Cinco", "Seis", "Sete", "Oito", "Nove", "Dez", "Onze",
                        "Doze", "Treze", "Quatorze", "Quinze", "Dezesseis", "Dezessete", "Dezoito", "Dezenove"]
        Dezenas = ["", "", "Vinte", "Trinta", "Quarenta", "Cinquenta", "Sessenta", "Setenta", "Oitenta", "Noventa"]
        Centenas = {"Cento", "Duzentos", "Trezentos", "Quatrocentos", "Quinhentos", "Seiscentos", "Setecentos",
                    "Oitocentos", "Novecentos"}
        PotenciasSingular = ["", " Mil", " Milhão", " Bilhão", " Trilhão", " Quatrilhão"]
        PotenciasPlural = ["", " Mil", " Milhões", " Bilhões", " Trilhões", " Quatrilhões"]
    
        strvalor = left("{:18,.3f})".format(valor), 18)

        for posicao in range(1, 18, 3): # For posicao = 1 To 18 Step 3

            print("posicao {}".format(posicao))
            print("mid {}".format(strvalor))
            parcial = val(mid(strvalor, posicao, 3))

            print("parcial {}".format(parcial))

            if parcial:
                if parcial == 1:
                    Buf = "Um {}".format(PotenciasSingular[int((18 - posicao) /3)])
                elif parcial == 100 :
                    Buf = "Cem {} ".format(PotenciasSingular[int((18 - posicao) / 3)])
                else:
                    Buf = Centenas[int(parcial / 100)]
                    parcial = parcial % 100
                    if parcial != 0 and Buf != "" :
                        Buf += " e "

                    if parcial < 20 :
                        Buf +=  Unidades[parcial]
                    else:
                        Buf += Dezenas[int(parcial / 10)]
                        parcial = parcial % 10
                        if parcial != 0 and Buf != "" :
                            Buf +=  " e "
                       
                        Buf += Unidades[parcial]
                    
                    Buf += PotenciasPlural[int((18 - posicao) / 3)]
            
            if Buf != "" :
                if extenso != "" :

                    parcial = val(mid(strvalor, posicao, 3))
                    if posicao == 16 and (parcial < 100 or (parcial % 100) == 0):
                        extenso += " e "
                    else:
                        extenso += ", "

                extenso = extenso + Buf
        # Next
        if extenso != "" :
            if Negativo:
                extenso += "Menos "
             
            if int(valor) == 1:
                extenso += " " + MoedaSingular
            else:
                extenso += " " + MoedaPlural
            
       
        parcial = int((valor - int(valor)) * 100 + Decimal(0.1))
        if parcial :
            Buf = extenso
            if extenso != "" :
                extenso +=  " e "
            extenso += Buf

        print(extenso)

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def val(data):
    y=0
    nst=""
    dlist = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9']
    for x in data:
        for i in dlist:
            if x == i:
                nst=nst+x
    n=len(nst)
    dcont=n
    acum=0
    for z in range(n):
        y=0
        for i in dlist:
            if nst[z] == i:
                d=y
                mult=1
                dcont=dcont-1
                for j in range(dcont):
                    mult=mult*10
                acum=acum+(d*mult)
            y=y+1

    return acum

extenso(10000.555, 'Metical', 'Meticais')