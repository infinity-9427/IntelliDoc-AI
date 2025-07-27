import { ReactNode } from "react";

type Props = {
  children?: ReactNode;
  title: ReactNode;
};

export default function PageLayout({ children, title }: Props) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#FFF] px-4 py-16">
      <div className="w-full max-w-4xl text-center">
        <h1 className="text-3xl font-bold text-white md:text-5xl">{title}</h1>
        <div className="mt-6 text-gray-400 md:text-lg">{children}</div>
      </div>
    </div>
  );
}

