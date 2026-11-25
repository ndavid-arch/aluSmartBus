import { useCallback, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { ApiError } from '../api/client'
import type { StopAhead } from '../api/live'
import {
  chooseStop,
  listJourneyStops,
  listMySelections,
  type JourneyStop,
  type Selection,
  type SelectionType,
} from '../api/selections'
import { CloseIcon } from './icons'

type Props = {
  journeyId: string
  token: string
  busLabel: string // "Bus 1 · Rebero → ALU"
  ahead: StopAhead[] // minutes to each stop ahead, from the live position
  onClose: () => void
}

// The words of each step: first where I get on, then where I get off
const STEPS: Record<SelectionType, { title: string; hint: string; action: string }> = {
  pickup: {
    title: 'Where do you get on?',
    hint: 'we alert you before it reaches your stop',
    action: 'as my stop',
  },
  dropoff: {
    title: 'Where do you get off?',
    hint: 'the driver sees where students get off',
    action: 'as where I get off',
  },
}

// "6 stops already passed · Rebero to Rwandex"
function passedSummary(passed: JourneyStop[]): string {
  if (passed.length === 0) return ''
  const plural = passed.length === 1 ? 'stop' : 'stops'
  const span =
    passed.length === 1 ? passed[0].name : `${passed[0].name} to ${passed[passed.length - 1].name}`
  return `${passed.length} ${plural} already passed · ${span}`
}

// Why a stop cannot be chosen in this step, or null when it can
function blockedReason(
  type: SelectionType,
  stop: JourneyStop,
  stops: JourneyStop[],
  pickup?: Selection,
): string | null {
  const last = stops[stops.length - 1]
  if (type === 'pickup' && stop.id === last?.id) return 'last stop'
  if (type === 'dropoff' && pickup) {
    const pickupIndex = stops.findIndex((candidate) => candidate.id === pickup.stop.id)
    if (stops.indexOf(stop) <= pickupIndex) return 'before your pickup'
  }
  return null
}

// The prototype's "Choose stop" screen (#71): stops ahead with their minutes, one to choose,
// first for getting on, then for getting off; passed stops are summed up in one line (#21)
function StopChooser({ journeyId, token, busLabel, ahead, onClose }: Props) {
  const [stops, setStops] = useState<JourneyStop[]>([])
  const [mine, setMine] = useState<Selection[]>([])
  const [chosenStep, setStep] = useState<SelectionType>('pickup')
  const [picked, setPicked] = useState<Partial<Record<SelectionType, string>>>({}) // not saved yet
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const pickup = mine.find((selection) => selection.type === 'pickup')
  // Once the bus is at my pickup stop (or it is too late), the pickup can no longer change
  const pickupSettled = pickup !== undefined && pickup.window_state !== 'waiting'

  // Load the stops (and which are passed) and my current choices
  const load = useCallback(() => {
    Promise.all([listJourneyStops(journeyId), listMySelections(journeyId, token)])
      .then(([journeyStops, selections]) => {
        setStops(journeyStops)
        setMine(selections)
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Could not load the stops.'))
  }, [journeyId, token])

  useEffect(load, [load])

  // Straight to the drop-off when the pickup can no longer change; my saved stop is pre-selected
  const step: SelectionType = pickupSettled ? 'dropoff' : chosenStep
  const saved = mine.find((selection) => selection.type === step)?.stop.id
  const choice = picked[step] ?? saved ?? null

  // Save the chosen stop, then go on to the drop-off (or close after it)
  async function handleSave() {
    if (!choice) return
    setSaving(true)
    setError('')
    try {
      const result = await chooseStop(journeyId, step, choice, token)
      setMine((current) => [...current.filter((s) => s.type !== step), result])
      if (step === 'pickup') setStep('dropoff')
      else onClose()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save your stop.')
      load() // the bus may have just passed it: refresh the list
    } finally {
      setSaving(false)
    }
  }

  const passed = stops.filter((stop) => stop.passed)
  const open = stops.filter((stop) => !stop.passed)
  const minutes = new Map(ahead.map((stop) => [stop.name, stop.minutes]))
  const chosenStop = stops.find((stop) => stop.id === choice)
  const words = STEPS[step]

  // Drawn at the top level of the page (a portal), so no map layer can sit above it
  return createPortal(
    <div className="chooser" role="dialog" aria-modal="true" aria-label={words.title}>
      <header className="chooser-head">
        <div>
          <h2>{words.title}</h2>
          <button type="button" className="icon-btn close" aria-label="Close" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <p>
          {busLabel} · {words.hint}
        </p>
      </header>

      {pickupSettled && step === 'dropoff' && (
        <p className="chooser-note">
          Your pickup is fixed: the bus has reached {pickup.stop.name}.
        </p>
      )}
      {passed.length > 0 && <p className="chooser-note">{passedSummary(passed)}</p>}

      <ul className="chooser-list">
        {open.map((stop) => {
          const blocked = blockedReason(step, stop, stops, pickup)
          const selected = stop.id === choice
          const away = minutes.get(stop.name)
          return (
            <li key={stop.id}>
              <label className={`${selected ? 'selected' : ''}${blocked ? ' blocked' : ''}`}>
                <input
                  type="radio"
                  name={`stop-${step}`}
                  value={stop.id}
                  checked={selected}
                  disabled={blocked !== null}
                  onChange={() => setPicked((current) => ({ ...current, [step]: stop.id }))}
                />
                <span className="chooser-name">{stop.name}</span>
                <span className="pill">
                  {blocked ?? (away === undefined ? '–' : away === 0 ? 'now' : `${away} min`)}
                </span>
              </label>
            </li>
          )
        })}
      </ul>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <div className="chooser-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!chosenStop || saving}
          onClick={handleSave}
        >
          {saving
            ? 'Saving…'
            : chosenStop
              ? `Set ${chosenStop.name} ${words.action}`
              : 'Choose a stop'}
        </button>
        {step === 'dropoff' && (
          <button type="button" className="link-button" onClick={onClose}>
            I will decide later
          </button>
        )}
      </div>
    </div>,
    document.body,
  )
}

export default StopChooser
