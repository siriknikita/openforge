"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export function MarkdownViewer({ content, className }: MarkdownViewerProps) {
  return (
    <div className={`markdown-content ${className || ""}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code: ({ className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || "");
            const isBlockCode = !!match;
            return isBlockCode ? (
              <pre className="bg-muted p-4 rounded-md overflow-x-auto">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            ) : (
              <code className="bg-muted px-1.5 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            );
          },
          a: ({ ...props }: any) => (
            <a className="text-primary hover:underline" {...props} />
          ),
          p: ({ ...props }: any) => (
            <p className="mb-4" {...props} />
          ),
          h1: ({ ...props }: any) => (
            <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />
          ),
          h2: ({ ...props }: any) => (
            <h2 className="text-xl font-bold mt-5 mb-3" {...props} />
          ),
          h3: ({ ...props }: any) => (
            <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />
          ),
          h4: ({ ...props }: any) => (
            <h4 className="text-base font-semibold mt-3 mb-2" {...props} />
          ),
          strong: ({ ...props }: any) => (
            <strong className="font-semibold" {...props} />
          ),
          em: ({ ...props }: any) => (
            <em className="italic" {...props} />
          ),
          hr: ({ ...props }: any) => (
            <hr className="my-4 border-border" {...props} />
          ),
          table: ({ ...props }: any) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-border" {...props} />
            </div>
          ),
          th: ({ ...props }: any) => (
            <th className="border border-border px-4 py-2 bg-muted font-semibold text-left" {...props} />
          ),
          td: ({ ...props }: any) => (
            <td className="border border-border px-4 py-2" {...props} />
          ),
          img: ({ ...props }: any) => (
            <img className="max-w-full h-auto rounded-md my-4" {...props} />
          ),
          ul: ({ ...props }: any) => (
            <ul className="list-disc pl-6 space-y-1" {...props} />
          ),
          ol: ({ ...props }: any) => (
            <ol className="list-decimal pl-6 space-y-1" {...props} />
          ),
          blockquote: ({ ...props }: any) => (
            <blockquote className="border-l-4 border-muted-foreground pl-4 italic" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

