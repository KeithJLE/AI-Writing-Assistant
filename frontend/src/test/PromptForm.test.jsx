import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PromptForm from '../components/PromptForm/PromptForm.jsx'

describe('PromptForm', () => {
  const defaultProps = {
    value: '',
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    onCancel: vi.fn(),
    isProcessing: false,
    state: 'idle',
    maxLength: 600,
  }

  it('renders correctly', () => {
    render(<PromptForm {...defaultProps} />)
    
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /process/i })).toBeInTheDocument()
  })

  it('displays the correct status message', () => {
    render(<PromptForm {...defaultProps} />)
    
    expect(screen.getByText('Ready to rephrase your writing.')).toBeInTheDocument()
  })

  it('displays processing status when processing', () => {
    render(<PromptForm {...defaultProps} isProcessing={true} state="processing" />)
    
    expect(screen.getByText('Streaming rephrased versions from OpenAI...')).toBeInTheDocument()
  })

  it('calls onChange when user types', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    
    render(<PromptForm {...defaultProps} onChange={onChange} />)
    
    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Hello world')
    
    expect(onChange).toHaveBeenCalled()
  })

  it('calls onSubmit when form is submitted with valid text', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<PromptForm {...defaultProps} value="Hello world" onSubmit={onSubmit} />)
    
    const submitButton = screen.getByRole('button', { name: /process/i })
    await user.click(submitButton)
    
    expect(onSubmit).toHaveBeenCalledWith('Hello world')
  })

  it('does not submit when text is empty', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<PromptForm {...defaultProps} value="" onSubmit={onSubmit} />)
    
    const submitButton = screen.getByRole('button', { name: /process/i })
    await user.click(submitButton)
    
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('does not submit when processing', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<PromptForm {...defaultProps} value="Hello" isProcessing={true} onSubmit={onSubmit} />)
    
    const submitButton = screen.getByRole('button', { name: /streaming/i })
    await user.click(submitButton)
    
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('shows cancel button when processing', () => {
    render(<PromptForm {...defaultProps} isProcessing={true} />)
    
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
  })

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup()
    const onCancel = vi.fn()
    
    render(<PromptForm {...defaultProps} isProcessing={true} onCancel={onCancel} />)
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)
    
    expect(onCancel).toHaveBeenCalled()
  })

  it('shows character counter', () => {
    render(<PromptForm {...defaultProps} value="Hello" />)
    
    expect(screen.getByText(/595.*characters left/)).toBeInTheDocument() // 600 - 5
  })

  it('shows warning when approaching character limit', () => {
    const longText = 'a'.repeat(580)
    render(<PromptForm {...defaultProps} value={longText} />)
    
    expect(screen.getByText(/20.*characters left/)).toBeInTheDocument()
  })
})