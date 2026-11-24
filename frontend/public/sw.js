// The service worker lets phones show SmartBus alerts (#25); tapping an alert opens the app
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    self.clients
      .matchAll({ type: 'window' })
      .then((windows) =>
        windows.length ? windows[0].focus() : self.clients.openWindow('/student'),
      ),
  )
})
