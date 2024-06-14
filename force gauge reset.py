import myForceGauge
from myForceGauge import ForceGauge_communication

fg = ForceGauge_communication()  # インスタンス化
fg.init('COM4')
fg.exit()