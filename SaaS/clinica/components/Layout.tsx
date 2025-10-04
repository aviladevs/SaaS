export default function Layout({ children }: LayoutProps) {
  return (
    <div className="bg-animated text-accent min-h-screen flex flex-col">
      {/* Overlay para deixar os cards legíveis */}
      <div className="backdrop-blur-sm bg-black/40 flex-1 flex flex-col">
        <header className="p-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-accent">
            Espaço Karen Martins
          </h1>
          <nav className="space-x-6">
            <Link href="/" className="hover:text-primary transition">Início</Link>
            <Link href="/servicos" className="hover:text-primary transition">Serviços</Link>
            <Link href="/agendar" className="hover:text-primary transition">Agendar</Link>
          </nav>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="p-4 text-center text-sm bg-black/60">
          © 2025 Espaço Karen Martins — Massoterapia Premium
        </footer>
      </div>
    </div>
  );
}
