import sys
sys.path.insert(0, '.')
import main
import inspect

r = main.app.routes[5]
print(f'Type: {type(r)}')
print(f'Module: {type(r).__module__}')
print(f'Attributes: {[a for a in dir(r) if not a.startswith("__")]}')
print()

# Try to find all attributes
for attr in dir(r):
    if not attr.startswith('_'):
        try:
            val = getattr(r, attr)
            print(f'  {attr}: {type(val).__name__} = {val}')
        except:
            print(f'  {attr}: <error>')

# Check if the included routers have routes
for i, route_obj in enumerate(main.app.routes):
    if type(route_obj).__name__ == '_IncludedRouter':
        print(f'\n_IncludedRouter [{i}]:')
        for attr in ['router', 'routes', '_routes']:
            if hasattr(route_obj, attr):
                val = getattr(route_obj, attr)
                print(f'  {attr}: {val}')
                if hasattr(val, '__iter__') and not isinstance(val, str):
                    for item in val:
                        print(f'    item: {type(item).__name__}')
                        if hasattr(item, 'path'):
                            print(f'      path: {item.path}')
