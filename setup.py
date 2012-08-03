from distutils.core import setup

setup(
    name='ShadowCraft-Engine',
    url='http://github.com/Aldriana/ShadowCraft-Engine/',
    version='0.1',
    packages=['shadowcraft',
        'shadowcraft.calcs', 'shadowcraft.calcs.rogue', 'shadowcraft.calcs.rogue.Aldriana',
        'shadowcraft.core',
        'shadowcraft.objects'],
    license='LGPL',
    long_description=open('README').read(),
)
