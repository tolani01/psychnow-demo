import { cn } from "../../lib/utils";

interface ChatBubbleProps {
  type: 'system' | 'patient' | 'options' | 'finish';
  children: React.ReactNode;
  className?: string;
  isHistorical?: boolean;
}

export function ChatBubble({ type, children, className, isHistorical }: ChatBubbleProps) {
  const isSystem = type === 'system' || type === 'options' || type === 'finish';
  
  return (
    <div className={cn(
      "w-full rounded-xl md:rounded-2xl px-3 py-2 md:px-4 md:py-3 transition-all text-base md:text-lg animate-fade-in",
      isSystem 
        ? "bg-blue-50 text-gray-900" 
        : "bg-blue-600 text-white",
      isHistorical && isSystem && "bg-gray-100 text-gray-500",
      isHistorical && !isSystem && "bg-blue-300 text-gray-700 font-normal",
      className
    )}>
      {children}
    </div>
  );
}

