import * as React from "react";
import { CheckCircle, XCircle } from "lucide-react";

export interface TevroxToastProps {
  /** Toast message */
  message: string;
  /** Toast type: success, error, info */
  type?: "success" | "error" | "info";
  /** Auto-dismiss timeout in ms */
  duration?: number;
  /** Whether manual close is allowed */
  closable?: boolean;
}

export function TevroxToast({
  message,
  type = "info",
  duration = 4000,
  closable = true,
}: TevroxToastProps) {
  const [isVisible, setIsVisible] = React.useState(true);
  const [closeTimeout, setCloseTimeout] = React.useState<number | null>(null);

  React.useEffect(() => {
    if (!isVisible) return;
    const timeout = setTimeout(() => setIsVisible(false), duration);
    setCloseTimeout(timeout);
    return () => clearTimeout(timeout);
  }, [isVisible, duration]);

  const handleClose = () => {
    setIsVisible(false);
    if (closeTimeout) clearTimeout(closeTimeout);
  };

  const typeStyles = {
    success: {
      bg: "var(--tevrox-success)",
      icon: <CheckCircle className="w-4 h-4 text-primary" />,
    },
    error: {
      bg: "var(--tevrox-danger)",
      icon: <XCircle className="w-4 h-4 text-white" />,
    },
    info: {
      bg: "var(--tevrox-info)",
      icon: null,
    },
  }[type];

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "fixed bottom-4 left-1/2 -translate-x-1/2 max-w-md w-full rounded-md shadow-lg px-4 py-3 flex items-center gap-3 transform transition-all duration-300",
        typeStyles.bg,
        "text-white",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2"
      )}
      role="alert"
      aria-live="polite"
    >
      {typeIcons[type.type] || typeStyles.icon}
      <span className="flex-1 whitespace-nowrap">{message}</span>
      {closable && (
        <button
          onClick={handleClose}
          className="ml-3 opacity-80 hover:opacity-100 transition-opacity"
          aria-label="Close toast"
        >
          ✕
        </button>
      )}
    </div>
  );
}