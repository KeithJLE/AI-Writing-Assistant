import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useRephrase } from '../hooks/useRephrase.js'

// Mock fetch
global.fetch = vi.fn()

// Mock EventSource
const mockEventSource = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  readyState: 1,
  onmessage: null,
  onerror: null
}

global.EventSource = vi.fn(() => mockEventSource)

describe('useRephrase', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ request_id: 'test-request-id' })
    })
    // Reset the mock EventSource
    mockEventSource.close.mockClear()
    mockEventSource.addEventListener.mockClear()
    mockEventSource.removeEventListener.mockClear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useRephrase())
    
    expect(result.current.state).toBe('idle')
    expect(result.current.isProcessing).toBe(false)
    expect(result.current.activeStyle).toBe(null)
    expect(result.current.outputs).toEqual({
      professional: '',
      casual: '',
      polite: '',
      social: ''
    })
  })

  it('processes text successfully', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    expect(fetch).toHaveBeenCalledWith('/v1/rephrase', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Hello world',
        styles: ['professional', 'casual', 'polite', 'social']
      })
    }))
    
    expect(result.current.state).toBe('processing')
    expect(result.current.isProcessing).toBe(true)
  })

  it('handles API errors gracefully', async () => {
    // Suppress console.error for this test
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    fetch.mockRejectedValueOnce(new Error('API Error'))
    
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    expect(result.current.state).toBe('canceled')
    expect(result.current.isProcessing).toBe(false)
    
    // Restore console.error
    consoleErrorSpy.mockRestore()
  })

  it('cancels processing correctly', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    expect(result.current.isProcessing).toBe(true)
    expect(result.current.state).toBe('processing')
    
    await act(async () => {
      await result.current.cancel()
    })
    
    expect(result.current.state).toBe('canceled')
    expect(result.current.isProcessing).toBe(false)
    // The EventSource should be created and then closed during cancel
    expect(EventSource).toHaveBeenCalled()
  })

  it('resets state correctly', () => {
    const { result } = renderHook(() => useRephrase())
    
    // First set some state
    act(() => {
      result.current.outputs.professional = 'Some text'
    })
    
    act(() => {
      result.current.reset()
    })
    
    expect(result.current.state).toBe('idle')
    expect(result.current.outputs).toEqual({
      professional: '',
      casual: '',
      polite: '',
      social: ''
    })
    expect(result.current.activeStyle).toBe(null)
  })

  it('handles empty text input', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('')
    })
    
    expect(fetch).toHaveBeenCalledWith('/v1/rephrase', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: '',
        styles: ['professional', 'casual', 'polite', 'social']
      })
    }))
    expect(result.current.state).toBe('processing')
  })

  it('handles whitespace-only text input', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('   ')
    })
    
    expect(fetch).toHaveBeenCalledWith('/v1/rephrase', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: '   ',
        styles: ['professional', 'casual', 'polite', 'social']
      })
    }))
    expect(result.current.state).toBe('processing')
  })

  it('creates EventSource with correct URL', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    expect(EventSource).toHaveBeenCalledWith('/v1/rephrase/stream?request_id=test-request-id')
  })

  it('handles SSE delta events correctly', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    // Simulate receiving a delta event
    const deltaEvent = {
      data: JSON.stringify({
        type: 'delta',
        style: 'professional',
        text: 'Hello there'
      })
    }
    
    act(() => {
      // Call the onmessage handler directly
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage(deltaEvent)
      }
    })
    
    expect(result.current.outputs.professional).toBe('Hello there')
    expect(result.current.activeStyle).toBe('professional')
  })

  it('handles SSE complete events correctly', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    // Simulate receiving a complete event
    const completeEvent = {
      data: JSON.stringify({
        type: 'complete',
        style: 'professional'
      })
    }
    
    act(() => {
      // Call the onmessage handler directly
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage(completeEvent)
      }
    })
    
    expect(result.current.activeStyle).toBe(null)
  })

  it('handles SSE end events correctly', async () => {
    const { result } = renderHook(() => useRephrase())
    
    await act(async () => {
      await result.current.process('Hello world')
    })
    
    // Simulate receiving an end event
    const endEvent = {
      data: JSON.stringify({
        type: 'end'
      })
    }
    
    act(() => {
      // Call the onmessage handler directly
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage(endEvent)
      }
    })
    
    expect(result.current.state).toBe('done')
    expect(result.current.isProcessing).toBe(false)
  })
})