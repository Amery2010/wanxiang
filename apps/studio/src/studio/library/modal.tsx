import { useRef, type ReactNode, type RefObject } from "react";
import { Dialog, DialogContent, DialogTitle } from "../../ui/dialog";

export function LibraryModal({
  children,
  title,
  className,
  initialFocus,
  onClose,
}: {
  children: ReactNode;
  title: string;
  className: string;
  initialFocus: RefObject<HTMLElement | null>;
  onClose(): void;
}) {
  const previousFocus = useRef(document.activeElement as HTMLElement | null);
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent
        className={`${className} library-dialog-content`}
        showCloseButton={false}
        aria-describedby={undefined}
        onOpenAutoFocus={(event) => {
          if (initialFocus.current) {
            event.preventDefault();
            initialFocus.current.focus();
          }
        }}
        onCloseAutoFocus={(event) => {
          event.preventDefault();
          previousFocus.current?.focus();
        }}
      >
        <DialogTitle className="sr-only">{title}</DialogTitle>
        {children}
      </DialogContent>
    </Dialog>
  );
}
