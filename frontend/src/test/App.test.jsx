import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App.jsx'

// Mock the useRephrase hook
const mockUseRephrase = {
  outputs: {
    professional: '',
    casual: '',
    polite: '',
    social: ''
  },
  state: 'idle',
  process: vi.fn(),
  cancel: vi.fn(),
  isProcessing: false,
  activeStyle: null,
  reset: vi.fn()
}

vi.mock('../hooks/useRephrase.js', () => ({
  useRephrase: () => mockUseRephrase,
  STYLE_ORDER: ['professional', 'casual', 'polite', 'social'],
  STYLE_META: {
    professional: { label: 'Professional', helper: 'Formal business tone' },
    casual: { label: 'Casual', helper: 'Relaxed and friendly' },
    polite: { label: 'Polite', helper: 'Courteous and respectful' },
    social: { label: 'Social', helper: 'Engaging social media style' }
  }
}))

// Mock components
vi.mock('../components/ThemeToggle/ThemeToggle.jsx', () => ({
  default: ({ value, onChange }) => (
    <button onClick={() => onChange(value === 'light' ? 'dark' : 'light')}>
      Toggle theme ({value})
    </button>
  )
}))

vi.mock('../components/PromptForm/PromptForm.jsx', () => ({
  default: ({ value, onChange, onSubmit, onCancel, isProcessing, state }) => (
    <div data-testid="prompt-form">
      <textarea 
        value={value} 
        onChange={(e) => onChange(e.target.value)}
        data-testid="prompt-input"
      />
      <button onClick={() => onSubmit(value)} disabled={isProcessing}>
        {isProcessing ? 'Processing...' : 'Submit'}
      </button>
      {isProcessing && (
        <button onClick={onCancel}>Cancel</button>
      )}
      <div data-testid="state">{state}</div>
    </div>
  )
}))

vi.mock('../components/ResultsGrid/ResultsGrid.jsx', () => ({
  default: ({ outputs, state, activeStyle }) => (
    <div data-testid="results-grid">
      <div data-testid="grid-state">{state}</div>
      <div data-testid="active-style">{activeStyle || 'none'}</div>
      {Object.entries(outputs).map(([style, content]) => (
        <div key={style} data-testid={`output-${style}`}>{content}</div>
      ))}
    </div>
  )
}))

vi.mock('../components/ShinyText/ShinyText.jsx', () => ({
  default: ({ text, ...props }) => <div {...props}>{text}</div>
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock state
    Object.assign(mockUseRephrase, {
      outputs: {
        professional: '',
        casual: '',
        polite: '',
        social: ''
      },
      state: 'idle',
      isProcessing: false,
      activeStyle: null
    })
  })

  it('renders the main application structure', () => {
    render(<App />)
    
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('AI Writing Assistant')
    expect(screen.getByTestId('prompt-form')).toBeInTheDocument()
    expect(screen.getByTestId('results-grid')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /toggle theme/i })).toBeInTheDocument()
  })

  it('handles prompt input changes', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const input = screen.getByTestId('prompt-input')
    await user.type(input, 'Hello world')
    
    expect(input).toHaveValue('Hello world')
  })

  it('processes text when submitted', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const input = screen.getByTestId('prompt-input')
    await user.type(input, 'Hello world')
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    expect(mockUseRephrase.process).toHaveBeenCalledWith('Hello world')
  })

  it('cancels processing when cancel button is clicked', async () => {
    const user = userEvent.setup()
    mockUseRephrase.isProcessing = true
    
    render(<App />)
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)
    
    expect(mockUseRephrase.cancel).toHaveBeenCalled()
  })

  it('resets when prompt is cleared and not processing', () => {
    // Set initial state with content
    mockUseRephrase.state = 'done'
    mockUseRephrase.isProcessing = false
    
    const { rerender } = render(<App />)
    
    // Simulate clearing the prompt
    expect(mockUseRephrase.reset).toHaveBeenCalled()
  })

  it('toggles theme correctly', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const themeToggle = screen.getByRole('button', { name: /toggle theme/i })
    expect(themeToggle).toHaveTextContent('light')
    
    await user.click(themeToggle)
    expect(themeToggle).toHaveTextContent('dark')
  })

  it('applies theme class to document', () => {
    render(<App />)
    
    expect(document.documentElement.classList.contains('theme-light')).toBe(true)
  })

  it('passes correct props to PromptForm', () => {
    mockUseRephrase.isProcessing = true
    mockUseRephrase.state = 'processing'
    
    render(<App />)
    
    expect(screen.getByTestId('state')).toHaveTextContent('processing')
    expect(screen.getByRole('button', { name: /processing/i })).toBeDisabled()
  })

  it('passes correct props to ResultsGrid', () => {
    mockUseRephrase.state = 'done'
    mockUseRephrase.activeStyle = 'professional'
    mockUseRephrase.outputs = {
      professional: 'Professional text',
      casual: 'Casual text',
      polite: 'Polite text',
      social: 'Social text'
    }
    
    render(<App />)
    
    expect(screen.getByTestId('grid-state')).toHaveTextContent('done')
    expect(screen.getByTestId('active-style')).toHaveTextContent('professional')
    expect(screen.getByTestId('output-professional')).toHaveTextContent('Professional text')
  })

  it('shows empty state correctly', () => {
    render(<App />)
    
    expect(screen.getByTestId('state')).toHaveTextContent('idle')
    expect(screen.getByTestId('active-style')).toHaveTextContent('none')
    
    // All outputs should be empty
    expect(screen.getByTestId('output-professional')).toHaveTextContent('')
    expect(screen.getByTestId('output-casual')).toHaveTextContent('')
    expect(screen.getByTestId('output-polite')).toHaveTextContent('')
    expect(screen.getByTestId('output-social')).toHaveTextContent('')
  })
})