from mdast_cli.distribution_systems.google_play import GooglePlay
from mdast_cli.distribution_systems.rustore import get_app_info
from mdast_cli.distribution_systems.appstore import AppStore

# Rustore check

rustore_monitoring_result = get_app_info('ru.sberbankmobile')

print(rustore_monitoring_result)

# Google Play check

google_play = GooglePlay(None, None, 3624774396276758027, 'OAhOZ5UEld24PI_fb3KoM4orFft5bwEhTnSJuwgpr_lFM_IJncWlt6qdsp1YASKVjr706g.')
google_play_monitoring_result = google_play.get_app_info('ru.dodopizza.app')

print(google_play_monitoring_result)

#AppStore check

appstore = AppStore('sting.ios.apple@gmail.com', 'T9Vr382j2M8z596944')
app_store_monitoring_result = appstore.get_app_info(bundle_id='ru.yoo.money')

print(app_store_monitoring_result)
