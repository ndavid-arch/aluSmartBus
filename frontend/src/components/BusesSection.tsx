import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { listBuses, type Bus, type BusStatus } from '../api/buses'
import BusList from './BusList'
import RegisterBusForm from './RegisterBusForm'

type Props = {
  token: string
}

// Keep the list in plate order, like the backend sends it
function byPlate(buses: Bus[]): Bus[] {
  return [...buses].sort((a, b) => a.plate_number.localeCompare(b.plate_number))
}

// The buses part of the admin page: register buses, change capacity, print QR codes (#13)
function BusesSection({ token }: Props) {
  const [buses, setBuses] = useState<Bus[]>([])
  const [loadError, setLoadError] = useState('')

  // Load the buses once when the section opens
  useEffect(() => {
    listBuses(token)
      .then(setBuses)
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : 'Could not load buses.'))
  }, [token])

  // Add a newly registered bus to the list
  function handleRegistered(bus: Bus) {
    setBuses((current) => byPlate([...current, bus]))
  }

  // Merge in what changed (capacity or status); the QR code the admin sees is kept
  function handleChanged(updated: BusStatus) {
    setBuses((current) =>
      current.map((bus) => (bus.id === updated.id ? { ...bus, ...updated } : bus)),
    )
  }

  return (
    <>
      <RegisterBusForm token={token} onRegistered={handleRegistered} />
      <h2>Buses</h2>
      {loadError ? (
        <p className="error">{loadError}</p>
      ) : (
        <BusList buses={buses} token={token} onChanged={handleChanged} />
      )}
    </>
  )
}

export default BusesSection
