// Icônes au trait, reprises de la maquette. Décoratives : aria-hidden.
function Icon({ size = 18, strokeWidth = 2, children }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {children}
    </svg>
  );
}

export const PlusIcon = ({ size = 18 }) => (
  <Icon size={size} strokeWidth={size < 16 ? 2.4 : 2}><path d="M12 5v14M5 12h14" /></Icon>
);

export const FicheIcon = () => (
  <Icon size={15}>
    <path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z" />
    <path d="M14 3v5h5M9 13h6M9 17h4" />
  </Icon>
);

export const QuizIcon = () => (
  <Icon size={15}>
    <path d="M9 6h11M9 12h11M9 18h11" />
    <path d="M4 6l1 1 2-2M4 12l1 1 2-2M4 18l1 1 2-2" />
  </Icon>
);

export const SendIcon = () => (
  <Icon size={20} strokeWidth={2.2}><path d="M5 12h14M13 6l6 6-6 6" /></Icon>
);

export const CloseIcon = ({ size = 18 }) => (
  <Icon size={size} strokeWidth={size < 16 ? 2.4 : 2}><path d="M6 6l12 12M18 6L6 18" /></Icon>
);
