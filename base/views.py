from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.http import HttpResponse, JsonResponse # type: ignore
from .models import Estado, Municipio, Contato, Interesse, Partido, Email, Telephone, Cargo #,Telefone, Email
from .forms import  ContactForm,  EmailFormSet, TelephoneFormSet#, EditContactForm, EditEmailForm, EditTelephoneForm#, EmailEntryForm#, EmailFormset, TelefoneFormset
import csv
import json
import os
from django.conf import settings




def loginPage(request):
    page = 'login'


    if request.user.is_authenticated: 
        return redirect('home')


    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')
    
    context = {'page': page}
    return render(request, 'base/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url= 'login')
def homePage(request):
    estados = Estado.objects.all().order_by('nome')  # Busca todos os estados do banco de dados
    partidos = Partido.objects.all().order_by('nome')
    cargos = Cargo.objects.all()

    if request.method == 'POST':

        # Processa o formulário de contato principal
        contact_form = ContactForm(request.POST, request.FILES)
        if contact_form.is_valid():
            contact = contact_form.save()

            # Salva o campo principal de email e telefone, se existirem
            if request.POST.get('emails'):
                Email.objects.create(contact=contact, email=request.POST.get('emails'))

            if request.POST.get('telephones'):
                Telephone.objects.create(contact=contact, telephone=request.POST.get('telephones'))

            # Processa os emails adicionais
            additional_emails = request.POST.getlist('additional_emails')
            for email in additional_emails:
                if email:  # Evita salvar campos vazios
                    Email.objects.create(contact=contact, email=email)

            # Processa os telefones adicionais
            additional_telephones = request.POST.getlist('additional_telephones')
            for telephone in additional_telephones:
                if telephone:  # Evita salvar campos vazios
                    Telephone.objects.create(contact=contact, telephone=telephone)

            return redirect('home')  # Redireciona para uma página de sucesso ou lista de contatos

    else:
        contact_form = ContactForm()

    return render(request, 'base/sidebar.html', {'form': contact_form, 'estados': estados, 'partidos': partidos, 'cargos': cargos})

def get_municipios(request, estado_id):
    # Busca os municípios relacionados ao estado_id
    municipios = Municipio.objects.filter(estado_id=estado_id).values('id', 'nome')
    
    # Verifique o formato solicitado na URL (ex: ?format=dash ou ?format=home)
    format_type = request.GET.get('format', 'home')  # Valor padrão é 'home'

    # Resposta específica para o formato 'dash'
    if format_type == 'dash':
        return JsonResponse(list(municipios), safe=False)

    # Resposta padrão para o formato 'home'
    return JsonResponse({'municipios': list(municipios)}, safe=False)

@login_required(login_url='login')
def dashPage(request):
    cargo = request.GET.get('cargo')
    estado = request.GET.get('estado')
    municipio = request.GET.get('municipio')
    busca = request.GET.get('busca')

    # Filtrando os contatos
    contatos = Contato.objects.all()

    if cargo:
        contatos = contatos.filter(cargo_id=cargo)
    if estado:
        contatos = contatos.filter(estado_id=estado)
    if municipio:
        contatos = contatos.filter(municipio_id=municipio)
    if busca:
        contatos = contatos.filter(nome__icontains=busca)

    # Carregando os valores para os filtros
    cargos_disponiveis = Cargo.objects.all()
    estados_disponiveis = Estado.objects.all().order_by('nome') 
    municipios_disponiveis = Municipio.objects.all()

    context = {
        'contatos': contatos,
        'cargos_disponiveis': cargos_disponiveis,
        'estados_disponiveis': estados_disponiveis,
        'municipios_disponiveis': municipios_disponiveis
    }

    return render(request, 'base/dash.html', context)


@login_required(login_url='login')
def editar_contato(request, contato_id):
    # Busca o contato pelo ID
    contato = get_object_or_404(Contato, id=contato_id)
    todos_interesses = Interesse.objects.all()  # Obtém todos os interesses disponíveis
    emails = Email.objects.filter(contact = contato)
    telefones = Telephone.objects.filter(contact = contato)


    if request.method == 'POST':
        # Processa os dados de edição
        contato.nome = request.POST.get('nome')
        contato.entidade = request.POST.get('entidade')

        # Busca o cargo correto no banco de dados pelo ID
        cargo_id = request.POST.get('cargo')
        cargo = get_object_or_404(Cargo, id=cargo_id)
        contato.cargo = cargo



        # Busca o partido correto no banco de dados pelo ID
        partido_id = request.POST.get('partido')
        partido = get_object_or_404(Partido, id=partido_id)
        contato.partido = partido

        # Busca o estado correto no banco de dados pelo ID
        estado_id = request.POST.get('estado')
        estado = get_object_or_404(Estado, id=estado_id)
        contato.estado = estado

        # Busca o município correto no banco de dados pelo ID
        municipio_id = request.POST.get('municipio')
        municipio = get_object_or_404(Municipio, id=municipio_id)
        contato.municipio = municipio
        
         # Atualiza os interesses
        interesses_ids = request.POST.getlist('interesses')  # Usa getlist para múltiplos valores
        contato.interesses.set(interesses_ids)  # Define os interesses

        # Atualiza os emails
        for email in emails:
            email_field_name = f'email_{email.id}'
            email_address = request.POST.get(email_field_name)
            if email_address:
                email.email = email_address
                email.save()

                # Atualiza os emails
        for telefone in telefones:
            telefone_field_name = f'telefone_{telefone.id}'
            telefone_number = request.POST.get(telefone_field_name)
            if  telefone_number:
                telefone.telephone = telefone_number
                telefone.save()
        

        contato.save()  # Salva as mudanças
        return redirect('dash')  # Redireciona de volta para o dashboard

    # Carrega todos os estados
    estados_disponiveis = Estado.objects.all().order_by('nome')
    partidos_disponiveis = Partido.objects.all().order_by('nome')

    # Carrega todos os cargos
    cargos_disponiveis = Cargo.objects.all()
    # Carrega os municípios apenas do estado atual do contato
    municipios_disponiveis = Municipio.objects.filter(estado=contato.estado)

    context = {
        'contato': contato,
        'emails': emails,
        'telefones': telefones,
        'estados_disponiveis': estados_disponiveis,
        'municipios_disponiveis': municipios_disponiveis,  # Somente os municípios do estado atual
        'todos_interesses': todos_interesses,  # Passa os interesses disponíveis para o template
        'partidos_disponiveis': partidos_disponiveis,
        'cargos_disponiveis': cargos_disponiveis,
    }

    return render(request, 'base/editar_contato.html', context)


@login_required(login_url='login')
def edit_profile(request, contato_id):
    # Busca o contato pelo ID
    contato = get_object_or_404(Contato, id=contato_id)
    todos_interesses = Interesse.objects.all()  # Obtém todos os interesses disponíveis


    if request.method == 'POST':
        # Processa os dados de edição
        contato.nome = request.POST.get('nome')
        contato.email = request.POST.get('email')
        contato.cargo = request.POST.get('cargo')
        contato.telefone = request.POST.get('telefone')
        contato.celular = request.POST.get('celular')
        contato.entidade = request.POST.get('entidade')

        # Busca o partido correto no banco de dados pelo ID
        partido_id = request.POST.get('partido')
        partido = get_object_or_404(Partido, id=partido_id)
        contato.partido = partido

        # Busca o estado correto no banco de dados pelo ID
        estado_id = request.POST.get('estado')
        estado = get_object_or_404(Estado, id=estado_id)
        contato.estado = estado

        # Busca o município correto no banco de dados pelo ID
        municipio_id = request.POST.get('municipio')
        municipio = get_object_or_404(Municipio, id=municipio_id)
        contato.municipio = municipio
        
         # Atualiza os interesses
        interesses_ids = request.POST.getlist('interesses')  # Usa getlist para múltiplos valores
        contato.interesses.set(interesses_ids)  # Define os interesses
        contato.save()
        contato.save()  # Salva as mudanças
        return redirect('dash')  # Redireciona de volta para o dashboard

    # Carrega todos os estados
    estados_disponiveis = Estado.objects.all().order_by('nome')
    partidos_disponiveis = Partido.objects.all().order_by('nome')


    # Carrega os municípios apenas do estado atual do contato
    municipios_disponiveis = Municipio.objects.filter(estado=contato.estado)

    context = {
        'contato': contato,
        'estados_disponiveis': estados_disponiveis,
        'municipios_disponiveis': municipios_disponiveis,  # Somente os municípios do estado atual
        'todos_interesses': todos_interesses,  # Passa os interesses disponíveis para o template
        'partidos_disponiveis': partidos_disponiveis
    }

    return render(request, 'base/profile.html', context)




def home(request):
    return HttpResponse("Home page")

@login_required(login_url='login')
def exportar_estados_csv(request):
    # Configura a resposta como um arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estados.csv"'

    # Cria um escritor CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome'])  # Cabeçalho do CSV

    # Itera sobre os estados e escreve as linhas
    for estado in Estado.objects.all():
        writer.writerow([estado.id, estado.nome])

    return response


@login_required(login_url='login')
def exportar_municipios_csv(request):
    # Configura a resposta como um arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="muns.csv"'

    # Cria um escritor CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome', "ID_Estado"])  # Cabeçalho do CSV

    # Itera sobre os estados e escreve as linhas
    for municipio in Municipio.objects.all():
        writer.writerow([municipio.id, municipio.nome, municipio.estado_id])

    return response



@login_required(login_url='login')
def exportar_cargos_csv(request):
    # Configura a resposta como um arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cargos.csv"'

    # Cria um escritor CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome'])  # Cabeçalho do CSV

    # Itera sobre os estados e escreve as linhas
    for cargo in Cargo.objects.all():
        writer.writerow([cargo.id, cargo.nome])

    return response

@login_required(login_url='login')
def exportar_partidos_csv(request):
    # Configura a resposta como um arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="partidos.csv"'

    # Cria um escritor CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome'])  # Cabeçalho do CSV

    # Itera sobre os estados e escreve as linhas
    for partido in Partido.objects.all():
        writer.writerow([partido.id, partido.nome])

    return response


def mapa_view(request):
    # Caminho para o arquivo GeoJSON
    geojson_path = os.path.join(settings.BASE_DIR, 'static\\geojson\\grandes_regioes_json.geojson')
    
    # Carregar o arquivo GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        mapa_brasil = json.load(f)
    
    # Dados de exemplo para cada região
    dados_regioes = [
        {"id": "N", "valor": 10, "nome": "Norte"},
        {"id": "NE", "valor": 20, "nome": "Nordeste"},
        {"id": "CO", "valor": 15, "nome": "Centro-Oeste"},
        {"id": "SE", "valor": 30, "nome": "Sudeste"},
        {"id": "S", "valor": 25, "nome": "Sul"}
    ]
    
    # Passar o GeoJSON e os dados para o template
    return render(request, 'base/mapa.html', {
        'mapa_brasil': json.dumps(mapa_brasil),  # Passar como JSON para o template
        'dados_regioes': json.dumps(dados_regioes)
    })