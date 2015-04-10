from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from .mail import StdoutMailer

from . import models
from . import views
from . import login
from . import schemas

from horus.interfaces import IRegisterSchema


def configure_horus(config):
    # Tell horus which SQLAlchemy scoped session to use:
    from hem.interfaces import IDBSession
    registry = config.registry
    registry.registerUtility(models.DBSession, IDBSession)

    config.include('horus')
    config.scan_horus(models)

    config.add_view('horus.views.AuthController', attr='login', route_name='login', renderer='login/login.html')
    #config.add_view('horus.views.RegisterController', attr='register', route_name='register', renderer='login/register.html')
    config.add_route('waiting_for_activation', '/waiting-for-activation')
    config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)

    login.activate_monkey_patch()


def configure_mailer(config):
    mailer = StdoutMailer()
    config.registry.registerUtility(mailer, IMailer)


def config_templates(config):

    # Jinja 2 templates as .html files
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_renderer('.txt')
    config.add_jinja2_search_path('pyramid_web20:templates', name='.html')
    config.add_jinja2_search_path('pyramid_web20:templates', name='.txt')

    config.include("pyramid_web20.views.templatecontext")

# Done by Horus already?
# def configure_auth(config):
#     config.add_request_method(request.augment_request_get_user, 'user', reify=True)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.bind = engine
    config = Configurator(settings=settings)

    config_templates(config)

    config.add_static_view('static', 'static', cache_max_age=3600)

    configure_horus(config)
    configure_mailer(config)

    config.add_route('home', '/')
    config.scan()
    config.scan(views)

    return config.make_wsgi_app()