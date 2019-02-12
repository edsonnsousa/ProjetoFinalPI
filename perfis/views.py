from django.shortcuts import render
from perfis.models import *
from django.shortcuts import redirect
from perfis.forms import *
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View
from django.core.paginator import Paginator, InvalidPage
from django.db import transaction
from django.contrib import messages


# Create your views here.

@transaction.atomic
@login_required
def index(request):
    form = PostForm()
    perfil_logado = Perfil.objects.get(id=request.user.perfil.id)
    perfis_nao_bloqueados = perfil_logado.contatos_nao_bloqueados

    page = request.GET.get("page", 1)
    paginator = Paginator(perfil_logado.minha_timeline.get_timeline(), 10)
    total = paginator.count

    try:
        timeline = paginator.page(page)
    except InvalidPage:
        timeline = paginator.page(1)

    contexto = {
        'perfis': perfis_nao_bloqueados,
        'perfil_logado': get_perfil_logado(request),
        'form': form,
        'timeline': timeline
    }

    return render(request, 'index.html', contexto)


@transaction.atomic
@login_required
def exibir_perfil(request, perfil_id):
    form = UploadFotoPerfilForm()
    perfil = Perfil.objects.get(id=perfil_id)
    perfil_logado = get_perfil_logado(request)
    posso_convidar = perfil_logado.pode_convidar(perfil)
    posso_bloquear = perfil_logado.pode_bloquear(perfil)
    posso_exibir = perfil_logado.pode_exibir(perfil)

    page = request.GET.get("page", 1)
    paginator = Paginator(perfil.minhas_postagens.all(), 10)
    total = paginator.count

    try:
        minhas_postagens = paginator.page(page)
    except InvalidPage:
        minhas_postagens = paginator.page(1)

    contexto = {'perfil': perfil,
                'perfil_logado': perfil_logado,
                'posso_convidar': posso_convidar,
                'posso_bloquear': posso_bloquear,
                'posso_exibir': posso_exibir,
                'minhas_postagens': minhas_postagens,
                'form': form
                }

    return render(request, 'perfil.html', contexto)


@login_required
def convidar(request, perfil_id):
    perfil_a_convidar = Perfil.objects.get(id=perfil_id)
    perfil_logado = get_perfil_logado(request)

    if (perfil_logado.pode_convidar(perfil_a_convidar)):
        perfil_logado.convidar(perfil_a_convidar)

    messages.success(request, 'Sucesso,convite enviado!')

    return redirect('index')


@login_required
def desfazer(request, perfil_id):
    perfil_logado = get_perfil_logado(request)
    perfil_logado.desfazer_amizade(perfil_id)
    messages.warning(request, 'Feito')
    return redirect('index')


@login_required
def get_perfil_logado(request):
    return request.user.perfil


@login_required
def aceitar(request, convite_id):
    convite = Convite.objects.get(id=convite_id)
    convite.aceitar()
    messages.success(request, 'Agora vocês são amigos')
    return redirect('index')


@login_required
def recusar(request, convite_id):
    convite = Convite.objects.get(id=convite_id)
    convite.recusar()
    messages.warning(request, 'Convite recusado')

    return redirect('index')


@login_required
def redefinir_senha(request):
    perfil_logado = get_perfil_logado(request)
    perfil_logado.redefinir_senha()


@transaction.atomic
@login_required
def setarSuperUsuario(request, perfil_id):
    perfil = Perfil.objects.get(id=perfil_id)
    perfil.usuario.is_superuser = True
    perfil.usuario.save()
    perfil.save()
    messages.success(request, 'Agora esse perfil é super usuario')
    return redirect('index')


@login_required
def bloquear(request, perfil_id):
    perfil_logado = get_perfil_logado(request)
    perfil_logado.bloquear_contatos(perfil_id)
    messages.warning(request, 'Bloqueado')
    return redirect('index')


@login_required
def desbloquear(request, bloqueio_id):
    bloqueio = Bloqueio.objects.get(id=bloqueio_id)
    bloqueio.desbloquear()
    messages.success(request, 'Perfil desbloqueado!')
    return redirect('index')


@login_required
def deletar_postagem(request, postagem_id):
    postagem = Postagem.objects.get(id=postagem_id)
    postagem.excluir_postagem()
    messages.warning(request, 'Post deletado')
    return redirect('index')


@login_required
def deletar_comentario(request, comentario_id):
    comentario = Postagem.objects.get(id=comentario_id)
    comentario.excluir_postagem()
    messages.warning(request, 'Comentario deletado')
    return redirect('index')


@login_required
def curtir(request, post_id):
    post = Postagem.objects.get(id=post_id)
    curtida = Curtida()
    curtida.post = post
    curtida.curtidor = get_perfil_logado(request)
    curtida.save()
    return redirect('index')


@login_required
def descurtir(request, post_id):
    postagem = Postagem.objects.get(id=post_id)
    curtida = Curtida.objects.get(post=postagem, curtidor=get_perfil_logado(request))
    curtida.post = postagem
    curtida.descurtir()
    return redirect('index')

@login_required
def alterar_foto_perfil(request):
    return render(request, 'alterar_foto_perfil.html', {'perfil_logado': get_perfil_logado(request)})


@login_required
def desativar_conta(request):
    messages.warning(request, 'Atenção! Conta desativada')
    return render(request, 'desativar_conta.html', {'perfil_logado': get_perfil_logado(request)})


@transaction.atomic
def transacao(request):
    form = UploadFotoPerfilForm()
    perfil_logado = get_perfil_logado(request)

    perfil_logado.nome = 'jose'
    perfil_logado.save()

    perfil_logado = 'a'

    perfil_logado.nome = 'maria'
    perfil_logado.save()

    page = request.GET.get("page", 1)
    paginator = Paginator(perfil_logado.minhas_postagens.all(), 10)
    total = paginator.count

    try:
        minhas_postagens = paginator.page(page)
    except InvalidPage:
        minhas_postagens = paginator.page(1)

    contexto = {'perfil': perfil_logado,
                'perfil_logado': perfil_logado,
                'posso_convidar': False,
                'posso_bloquear': False,
                'posso_exibir': True,
                'minhas_postagens': minhas_postagens,
                'form': form
                }

    return render(request, 'perfil.html', contexto)

    return


def ativar_conta(request):
    form = AtivarContaForm()
    return render(request, 'ativar_conta.html', {'form': form})


class AtivarContaView(View):
    @transaction.atomic
    def post(self, request):
        form = AtivarContaForm(request.POST)
        if form.is_valid():
            dados_form = form.cleaned_data
            perfil = Perfil.objects.get(nome=dados_form['nome'])
            perfil.usuario.is_active = True
            perfil.usuario.save()

            return redirect('index')

        return render(request, 'ativar_conta.html', {'form': form})


class DesativarContaView(View):
    @transaction.atomic
    def post(self, request):
        form = DesativarContaForm(request.POST)
        if form.is_valid():
            dados_form = form.cleaned_data
            perfil_logado = get_perfil_logado(request)
            perfil_logado.justificativa = dados_form['justificativa']
            perfil_logado.usuario.is_active = False
            perfil_logado.save()
            perfil_logado.usuario.save()

            return redirect('index')

        return redirect('index')


class PerfilView(View):

    def get(self, request):
        form = UploadFotoPerfilForm()
        perfil_logado = get_perfil_logado(request)

        page = request.GET.get("page", 1)
        paginator = Paginator(perfil_logado.minhas_postagens.all(), 10)
        total = paginator.count

        try:
            minhas_postagens = paginator.page(page)
        except InvalidPage:
            minhas_postagens = paginator.page(1)

        contexto = {'perfil': perfil_logado,
                    'perfil_logado': perfil_logado,
                    'posso_convidar': False,
                    'posso_bloquear': False,
                    'posso_exibir': True,
                    'form': form,
                    'minhas_postagens': minhas_postagens
                    }

        return render(request, 'perfil.html', contexto)

    @transaction.atomic
    def post(self, request):
        form = UploadFotoPerfilForm(request.POST, request.FILES)
        perfil_logado = get_perfil_logado(request)

        if form.is_valid():
            dados_form = form.cleaned_data
            perfil_logado.foto_perfil = dados_form['foto_perfil']
            perfil_logado.save()

            return redirect('index')

        form = UploadFotoPerfilForm()

        page = request.GET.get("page", 1)
        paginator = Paginator(perfil_logado.minhas_postagens.all(), 10)
        total = paginator.count

        try:
            minhas_postagens = paginator.page(page)
        except InvalidPage:
            minhas_postagens = paginator.page(1)

        contexto = {'perfil': perfil_logado,
                    'perfil_logado': perfil_logado,
                    'posso_convidar': False,
                    'posso_bloquear': False,
                    'posso_exibir': True,
                    'form': form,
                    'minhas_postagens': minhas_postagens
                    }

        return render(request, 'perfil.html', contexto)


class PostarView(View):
    @transaction.atomic
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            dados_form = form.cleaned_data
            print(dados_form)
            postagem = Postagem()
            postagem.dono = get_perfil_logado(request)
            postagem.imagem_postagem = dados_form['imagem_postagem']
            postagem.texto = dados_form['texto']
            postagem.save()
            return redirect('index')

        return redirect('index')


class PesquisarPerfilView(View):
    @transaction.atomic
    def post(self, request):
        form = PesquisaUsuarioForm(request.POST)

        if form.is_valid():
            dados_form = form.cleaned_data
            perfil_logado = get_perfil_logado(request)
            perfis_acessiveis = perfil_logado.pesquisar(dados_form['nome'])

            return render(request, 'pesquisa.html',
                          {'perfis': perfis_acessiveis, 'perfil_logado': get_perfil_logado(request)})

        return redirect('index')


def comentar_postagem(request, post_id):
    form = ComentarForm()
    post = Postagem.objects.get(id=post_id)
    perfil_logado = get_perfil_logado(request)
    return render(request, 'comentar.html', {'post': post, 'perfil_logado': perfil_logado, 'form': form})


class ComentarioView(View):
    def post(self, request, post_id):
        form = ComentarForm(request.POST)
        if form.is_valid():
            dados_form = form.cleaned_data
            post = Postagem.objects.get(id=post_id)
            comentario = Comentario()
            comentario.post = post
            comentario.texto = dados_form['texto']
            comentario.autor = get_perfil_logado(request)
            comentario.save()
        return redirect('index')
