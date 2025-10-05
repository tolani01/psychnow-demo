import { cn } from "../../lib/utils";

interface InputProps {
  placeholder?: string;
  value?: string;
  name?: string;
  id?: string;
  onKeyPress?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  type?: string;
  disabled?: boolean;
}

export function CustomInput({ placeholder, value, name, id, onKeyPress, onChange, className, type = "text", disabled }: InputProps) {
  return (
    <input
      id={id}
      name={name}
      type={type}
      placeholder={placeholder}
      value={value}
      disabled={disabled}
      onKeyPress={onKeyPress}
      onChange={onChange}
      className={cn(
        "h-11 w-full rounded-lg border border-gray-200 px-4 py-2 text-base",
        "placeholder:text-gray-600 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20",
        "disabled:bg-gray-100 disabled:cursor-not-allowed",
        className
      )}
    />
  );
}

