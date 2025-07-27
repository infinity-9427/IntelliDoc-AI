type Props = {
  href: string;
  title?: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
};

export default function ExternalLink({description, href, title, children, className}: Props) {
  // If children are provided, render as a simple inline link
  if (children) {
    return (
      <a
        className={className}
        href={href}
        rel="noreferrer"
        target="_blank"
      >
        {children}
      </a>
    );
  }

  // Original card-style link for when title and description are provided
  return (
    <a
      className="inline-block rounded-md border border-gray-700 p-8 transition-colors hover:border-gray-400"
      href={href}
      rel="noreferrer"
      target="_blank"
    >
      <p className="text-xl font-semibold text-white">
        {title} <span className="ml-2 inline-block">→</span>
      </p>
      <p className="mt-2 max-w-[250px] text-gray-400">{description}</p>
    </a>
  );
}
