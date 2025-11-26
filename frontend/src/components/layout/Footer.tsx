export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container py-6">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
            <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
              &copy; 2025 Sistema Reconhecimento Facial. Demo para controle de acesso.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
