import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import ResultsGrid from '../components/ResultsGrid/ResultsGrid.jsx'

// Mock the useRephrase hook data
vi.mock('../../hooks/useRephrase.js', () => ({
  STYLE_ORDER: ['professional', 'casual', 'polite', 'social'],
  STYLE_META: {
    professional: { label: 'Professional', helper: 'Formal business tone' },
    casual: { label: 'Casual', helper: 'Relaxed and friendly' },
    polite: { label: 'Polite', helper: 'Courteous and respectful' },
    social: { label: 'Social', helper: 'Engaging social media style' }
  }
}))

// Mock StyleCard component
vi.mock('../components/StyleCard/StyleCard.jsx', () => ({
  default: ({ style, label, content, isActive, state }) => (
    <div data-testid={`style-card-${style}`}>
      <h3>{label}</h3>
      <div data-testid="content">{content}</div>
      <div data-testid="status">{isActive ? 'active' : 'inactive'}</div>
      <div data-testid="state">{state}</div>
    </div>
  )
}))

describe('ResultsGrid', () => {
  const defaultProps = {
    outputs: {
      professional: '',
      casual: '',
      polite: '',
      social: ''
    },
    state: 'idle',
    activeStyle: null
  }

  it('renders the header correctly', () => {
    render(<ResultsGrid {...defaultProps} />)
    
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Rephrased styles')
    expect(screen.getByText(/Each writing style streams in real-time/)).toBeInTheDocument()
  })

  it('renders all style cards', () => {
    render(<ResultsGrid {...defaultProps} />)
    
    expect(screen.getByTestId('style-card-professional')).toBeInTheDocument()
    expect(screen.getByTestId('style-card-casual')).toBeInTheDocument()
    expect(screen.getByTestId('style-card-polite')).toBeInTheDocument()
    expect(screen.getByTestId('style-card-social')).toBeInTheDocument()
  })

  it('passes correct props to StyleCard components', () => {
    const outputs = {
      professional: 'Professional text here',
      casual: 'Casual text here',
      polite: 'Polite text here',
      social: 'Social text here'
    }

    render(<ResultsGrid {...defaultProps} outputs={outputs} activeStyle="professional" state="processing" />)
    
    // Check professional card is active
    const professionalCard = screen.getByTestId('style-card-professional')
    expect(professionalCard).toHaveTextContent('Professional')
    expect(professionalCard.querySelector('[data-testid="content"]')).toHaveTextContent('Professional text here')
    expect(professionalCard.querySelector('[data-testid="status"]')).toHaveTextContent('active')
    expect(professionalCard.querySelector('[data-testid="state"]')).toHaveTextContent('processing')
    
    // Check other cards are inactive
    const casualCard = screen.getByTestId('style-card-casual')
    expect(casualCard.querySelector('[data-testid="status"]')).toHaveTextContent('inactive')
  })

  it('displays empty content when no outputs', () => {
    render(<ResultsGrid {...defaultProps} />)
    
    const contentElements = screen.getAllByTestId('content')
    contentElements.forEach(element => {
      expect(element).toHaveTextContent('')
    })
  })

  it('shows active style correctly', () => {
    render(<ResultsGrid {...defaultProps} activeStyle="casual" />)
    
    const casualCard = screen.getByTestId('style-card-casual')
    expect(casualCard.querySelector('[data-testid="status"]')).toHaveTextContent('active')
    
    const professionalCard = screen.getByTestId('style-card-professional')
    expect(professionalCard.querySelector('[data-testid="status"]')).toHaveTextContent('inactive')
  })
})