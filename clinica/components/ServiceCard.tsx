import { ReactNode } from "react";

type ServiceCardProps = {
  title: string;
  description: string;
  icon?: ReactNode;
};

export default function ServiceCard({ title, description, icon }: ServiceCardProps) {
  return (
    <div className="bg-secondary p-6 rounded-2xl shadow-glow hover:scale-105 transition transform cursor-pointer border border-pink-500/30">
      <div className="flex items-center justify-center text-neon text-5xl mb-4">
        {icon}
      </div>
      <h3 className="text-2xl font-bold text-primary mb-2">{title}</h3>
      <p className="text-accent">{description}</p>
    </div>
  );
}

