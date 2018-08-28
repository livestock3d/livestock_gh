from lib.cmf import CMFModel

folder = r'C:\Users\Christian\Desktop\test_cmf\test_01'
mesh_path = folder + '/mesh.obj'
weather_path = folder + '/weather.xml'
m = CMFModel(mesh_path, weather_path)

m.create_weather()