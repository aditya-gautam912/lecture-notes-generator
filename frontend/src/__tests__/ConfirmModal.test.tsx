import { render, screen, fireEvent } from '@testing-library/react';
import ConfirmModal from '../components/ConfirmModal';

describe('ConfirmModal', () => {
  const baseProps = {
    open: true,
    title: 'Delete Lecture',
    message: 'Are you sure?',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing when closed', () => {
    const { container } = render(<ConfirmModal {...baseProps} open={false} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders title and message', () => {
    render(<ConfirmModal {...baseProps} />);
    expect(screen.getByText('Delete Lecture')).toBeInTheDocument();
    expect(screen.getByText('Are you sure?')).toBeInTheDocument();
  });

  it('calls onConfirm when confirm button clicked', () => {
    render(<ConfirmModal {...baseProps} />);
    fireEvent.click(screen.getByText('Delete'));
    expect(baseProps.onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button clicked', () => {
    render(<ConfirmModal {...baseProps} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(baseProps.onCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when overlay clicked', () => {
    render(<ConfirmModal {...baseProps} />);
    fireEvent.click(screen.getByRole('presentation'));
    expect(baseProps.onCancel).toHaveBeenCalledTimes(1);
  });
});
