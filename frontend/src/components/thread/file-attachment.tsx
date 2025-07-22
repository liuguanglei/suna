import React from 'react';
import Image from 'next/image';
import {
  FileText,
  FileImage,
  FileCode,
  FilePlus,
  FileSpreadsheet,
  FileVideo,
  FileAudio,
  FileType,
  Database,
  Archive,
  File,
  ExternalLink,
  Download,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { AttachmentGroup } from './attachment-group';
import { HtmlRenderer } from './preview-renderers/html-renderer';
import { MarkdownRenderer } from './preview-renderers/markdown-renderer';
import { CsvRenderer } from './preview-renderers/csv-renderer';
import { useFileContent, useImageContent } from '@/hooks/react-query/files';
import { useAuth } from '@/components/AuthProvider';
import { Project } from '@/lib/api';

// 定义基本文件类型
export type FileType =
  | 'image'
  | 'code'
  | 'text'
  | 'pdf'
  | 'audio'
  | 'video'
  | 'spreadsheet'
  | 'archive'
  | 'database'
  | 'markdown'
  | 'csv'
  | 'other';

// 基于扩展名的简单文件类型检测
function getFileType(filename: string): FileType {
  const ext = filename.split('.').pop()?.toLowerCase() || '';

  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(ext))
    return 'image';
  if (
    [
      'js',
      'jsx',
      'ts',
      'tsx',
      'html',
      'css',
      'json',
      'py',
      'java',
      'c',
      'cpp',
    ].includes(ext)
  )
    return 'code';
  if (['txt', 'log', 'env'].includes(ext)) return 'text';
  if (['md', 'markdown'].includes(ext)) return 'markdown';
  if (ext === 'pdf') return 'pdf';
  if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) return 'audio';
  if (['mp4', 'webm', 'mov', 'avi'].includes(ext)) return 'video';
  if (['csv', 'tsv'].includes(ext)) return 'csv';
  if (['xls', 'xlsx'].includes(ext)) return 'spreadsheet';
  if (['zip', 'rar', 'tar', 'gz'].includes(ext)) return 'archive';
  if (['db', 'sqlite', 'sql'].includes(ext)) return 'database';

  return 'other';
}

// 获取文件类型对应的图标
function getFileIcon(type: FileType): React.ElementType {
  const icons: Record<FileType, React.ElementType> = {
    image: FileImage,
    code: FileCode,
    text: FileText,
    markdown: FileText,
    pdf: FileType,
    audio: FileAudio,
    video: FileVideo,
    spreadsheet: FileSpreadsheet,
    csv: FileSpreadsheet,
    archive: Archive,
    database: Database,
    other: File,
  };

  return icons[type];
}

// 生成文件类型的可读标签
function getTypeLabel(type: FileType, extension?: string): string {
  if (type === 'code' && extension) {
    return extension.toUpperCase();
  }

  const labels: Record<FileType, string> = {
    image: '图片',
    code: '代码',
    text: '文本',
    markdown: 'Markdown',
    pdf: 'PDF',
    audio: '音频',
    video: '视频',
    spreadsheet: '表格',
    csv: 'CSV',
    archive: '压缩包',
    database: '数据库',
    other: '文件',
  };

  return labels[type];
}

// 根据文件路径和类型生成合理的文件大小
function getFileSize(filepath: string, type: FileType): string {
  // 基础大小计算
  const base = ((filepath.length * 5) % 800) + 200;

  // 类型特定的乘数
  const multipliers: Record<FileType, number> = {
    image: 5.0,
    video: 20.0,
    audio: 10.0,
    code: 0.5,
    text: 0.3,
    markdown: 0.3,
    pdf: 8.0,
    spreadsheet: 3.0,
    csv: 2.0,
    archive: 5.0,
    database: 4.0,
    other: 1.0,
  };

  const size = base * multipliers[type];

  if (size < 1024) return `${Math.round(size)} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

// 获取文件内容的 API URL
function getFileUrl(sandboxId: string | undefined, path: string): string {
  if (!sandboxId) return path;

  // 检查路径是否以 /workspace 开头
  if (!path.startsWith('/workspace')) {
    // 如果不是，则在路径前添加 /workspace
    path = `/workspace/${path.startsWith('/') ? path.substring(1) : path}`;
  }

  // 处理可能的 Unicode 转义序列
  try {
    // 将转义的 Unicode 序列替换为实际字符
    path = path.replace(/\\u([0-9a-fA-F]{4})/g, (_, hexCode) => {
      return String.fromCharCode(parseInt(hexCode, 16));
    });
  } catch (e) {
    console.error('处理路径中的 Unicode 转义时出错:', e);
  }

  const url = new URL(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/sandboxes/${sandboxId}/files/content`,
  );

  // 正确编码路径参数以支持 UTF-8
  url.searchParams.append('path', path);

  return url.toString();
}

interface FileAttachmentProps {
  filepath: string;
  onClick?: (path: string) => void;
  className?: string;
  sandboxId?: string;
  showPreview?: boolean;
  localPreviewUrl?: string;
  customStyle?: React.CSSProperties;
  /**
   * 控制 HTML、Markdown 和 CSV 文件是否显示内容预览。
   * - true: 文件以普通附件形式显示（默认）
   * - false: HTML、MD 和 CSV 文件在网格布局中显示渲染后的内容
   */
  collapsed?: boolean;
  project?: Project;
}

// 在挂载之间缓存获取的内容，避免重复请求
const contentCache = new Map<string, string>();
const errorCache = new Set<string>();

export function FileAttachment({
  filepath,
  onClick,
  className,
  sandboxId,
  showPreview = true,
  localPreviewUrl,
  customStyle,
  collapsed = true,
  project,
}: FileAttachmentProps) {
  // 身份验证
  const { session } = useAuth();

  // 简化的状态管理
  const [hasError, setHasError] = React.useState(false);

  // 基本文件信息
  const filename = filepath.split('/').pop() || '文件';
  const extension = filename.split('.').pop()?.toLowerCase() || '';
  const fileType = getFileType(filename);
  const fileUrl =
    localPreviewUrl || (sandboxId ? getFileUrl(sandboxId, filepath) : filepath);
  const typeLabel = getTypeLabel(fileType, extension);
  const fileSize = getFileSize(filepath, fileType);
  const IconComponent = getFileIcon(fileType);

  // 显示标志
  const isImage = fileType === 'image';
  const isHtmlOrMd =
    extension === 'html' ||
    extension === 'htm' ||
    extension === 'md' ||
    extension === 'markdown';
  const isCsv = extension === 'csv' || extension === 'tsv';
  const isGridLayout =
    customStyle?.gridColumn === '1 / -1' ||
    Boolean(customStyle && '--attachment-height' in customStyle);
  // 提前定义 isInlineMode，在任何 hooks 之前
  const isInlineMode = !isGridLayout;
  const shouldShowPreview =
    (isHtmlOrMd || isCsv) && showPreview && collapsed === false;

  // 使用 React Query hook 获取文件内容
  const {
    data: fileContent,
    isLoading: fileContentLoading,
    error: fileContentError,
  } = useFileContent(
    shouldShowPreview ? sandboxId : undefined,
    shouldShowPreview ? filepath : undefined,
  );

  // 使用 React Query hook 获取图片内容（带身份验证）
  const {
    data: imageUrl,
    isLoading: imageLoading,
    error: imageError,
  } = useImageContent(
    isImage && showPreview && sandboxId ? sandboxId : undefined,
    isImage && showPreview ? filepath : undefined,
  );

  // 根据查询错误设置错误状态
  React.useEffect(() => {
    if (fileContentError || imageError) {
      setHasError(true);
    }
  }, [fileContentError, imageError]);

  const handleClick = () => {
    if (onClick) {
      onClick(filepath);
    }
  };

  // 图片以其自然宽高比显示
  if (isImage && showPreview) {
    // 如果通过 CSS 变量提供了自定义高度，则用于图片
    const imageHeight = isGridLayout
      ? (customStyle['--attachment-height'] as string)
      : '54px';

    // 显示图片加载状态
    if (imageLoading && sandboxId) {
      return (
        <button
          onClick={handleClick}
          className={cn(
            'group relative min-h-[54px] min-w-fit rounded-xl cursor-pointer',
            'border border-black/10 dark:border-white/10',
            'bg-black/5 dark:bg-black/20',
            'p-0 overflow-hidden',
            'flex items-center justify-center',
            isGridLayout ? 'w-full' : 'min-w-[54px]',
            className,
          )}
          style={{
            maxWidth: '100%',
            height: isGridLayout ? imageHeight : 'auto',
            ...customStyle,
          }}
          title={filename}
        >
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
        </button>
      );
    }

    // 检查错误
    if (imageError || hasError) {
      return (
        <button
          onClick={handleClick}
          className={cn(
            'group relative min-h-[54px] min-w-fit rounded-xl cursor-pointer',
            'border border-black/10 dark:border-white/10',
            'bg-black/5 dark:bg-black/20',
            'p-0 overflow-hidden',
            'flex flex-col items-center justify-center gap-1',
            isGridLayout ? 'w-full' : 'inline-block',
            className,
          )}
          style={{
            maxWidth: '100%',
            height: isGridLayout ? imageHeight : 'auto',
            ...customStyle,
          }}
          title={filename}
        >
          <IconComponent className="h-6 w-6 text-red-500 mb-1" />
          <div className="text-xs text-red-500">加载图片失败</div>
        </button>
      );
    }

    return (
      <button
        onClick={handleClick}
        className={cn(
          'group relative min-h-[54px] rounded-xl cursor-pointer',
          'border border-black/10 dark:border-white/10',
          'bg-black/5 dark:bg-black/20',
          'p-0 overflow-hidden', // 无内边距，内容紧贴边框
          'flex items-center justify-center', // 图片居中
          isGridLayout ? 'w-full' : 'inline-block', // 网格中占满宽度
          className,
        )}
        style={{
          maxWidth: '100%', // 确保不超过容器宽度
          height: isGridLayout ? imageHeight : 'auto',
          ...customStyle,
        }}
        title={filename}
      >
        <img
          src={sandboxId && session?.access_token ? imageUrl : fileUrl}
          alt={filename}
          className={cn(
            'max-h-full', // 遵守父级高度限制
            isGridLayout ? 'w-full h-full object-cover' : 'w-auto', // 网格中占满宽度高度并使用 object-cover
          )}
          style={{
            height: imageHeight,
            objectPosition: 'center',
            objectFit: isGridLayout ? 'cover' : 'contain',
          }}
          onLoad={() => {
            console.log('图片加载成功:', filename);
          }}
          onError={(e) => {
            // 避免对同一图片的所有实例记录错误
            console.error('图片加载错误:', filename);

            // 仅在开发环境中记录详细信息，避免控制台垃圾信息
            if (process.env.NODE_ENV === 'development') {
              const imgSrc =
                sandboxId && session?.access_token ? imageUrl : fileUrl;
              console.error('图片 URL:', imgSrc);

              // 对 blob URL 的额外调试
              if (typeof imgSrc === 'string' && imgSrc.startsWith('blob:')) {
                console.error('Blob URL 加载失败。可能的原因：');
                console.error('- Blob URL 被过早撤销');
                console.error('- Blob 数据损坏或无效');
                console.error('- MIME 类型不匹配');

                // 尝试检查 blob URL 是否仍然有效
                fetch(imgSrc, { method: 'HEAD' })
                  .then((response) => {
                    console.error(`Blob URL HEAD 请求状态: ${response.status}`);
                    console.error(
                      `Blob URL 内容类型: ${response.headers.get('content-type')}`,
                    );
                  })
                  .catch((err) => {
                    console.error('Blob URL HEAD 请求失败:', err.message);
                  });
              }

              // 检查错误是否可能由于身份验证引起
              if (sandboxId && (!session || !session.access_token)) {
                console.error('身份验证问题：缺少会话或令牌');
              }
            }

            setHasError(true);
            // 如果图片加载失败且 localPreviewUrl 是 blob URL，则尝试直接使用它
            if (
              localPreviewUrl &&
              typeof localPreviewUrl === 'string' &&
              localPreviewUrl.startsWith('blob:')
            ) {
              console.log('回退到 localPreviewUrl:', filename);
              (e.target as HTMLImageElement).src = localPreviewUrl;
            }
          }}
        />
      </button>
    );
  }

  const rendererMap = {
    html: HtmlRenderer,
    htm: HtmlRenderer,
    md: MarkdownRenderer,
    markdown: MarkdownRenderer,
    csv: CsvRenderer,
    tsv: CsvRenderer,
  };

  // 当未折叠且处于网格布局时，显示 HTML/MD/CSV 预览
  if (shouldShowPreview && isGridLayout) {
    // 确定渲染器组件
    const Renderer = rendererMap[extension as keyof typeof rendererMap];

    return (
      <div
        className={cn(
          'group relative rounded-xl w-full',
          'border border-black/10 dark:border-white/10',
          'bg-black/5 dark:bg-black/20',
          'overflow-hidden',
          'h-[300px]', // 预览固定高度
          'pt-10', // 为标题留出空间
          className,
        )}
        style={{
          gridColumn: '1 / -1', // 在网格中占满宽度
          width: '100%', // 确保占满宽度
          ...customStyle,
        }}
        onClick={hasError ? handleClick : undefined} // 如果有错误则可点击
      >
        {/* 内容区域 */}
        <div className="h-full w-full relative">
          {/* 仅在无错误且有内容时显示内容 */}
          {!hasError && fileContent && (
            <>
              {Renderer ? (
                <Renderer
                  content={fileContent}
                  previewUrl={fileUrl}
                  className="h-full w-full"
                  project={project}
                />
              ) : (
                <div className="p-4 text-muted-foreground">
                  此文件类型无可用预览
                </div>
              )}
            </>
          )}

          {/* 错误状态 */}
          {hasError && (
            <div className="h-full w-full flex flex-col items-center justify-center p-4">
              <div className="text-red-500 mb-2">加载内容出错</div>
              <div className="text-muted-foreground text-sm text-center mb-2">
                {fileUrl && (
                  <div className="text-xs max-w-full overflow-hidden truncate opacity-70">
                    路径可能需要 /workspace 前缀
                  </div>
                )}
              </div>
              <button
                onClick={handleClick}
                className="px-3 py-1.5 bg-primary/10 hover:bg-primary/20 rounded-md text-sm"
              >
                在查看器中打开
              </button>
            </div>
          )}

          {/* 加载状态 */}
          {fileContentLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/50">
              <Loader2 className="h-6 w-6 text-primary animate-spin" />
            </div>
          )}

          {/* 空内容状态 - 当未加载且无内容时显示 */}
          {!fileContent && !fileContentLoading && !hasError && (
            <div className="h-full w-full flex flex-col items-center justify-center p-4 pointer-events-none">
              <div className="text-muted-foreground text-sm mb-2">预览可用</div>
              <div className="text-muted-foreground text-xs text-center">
                点击标题打开
              </div>
            </div>
          )}
        </div>

        {/* 带文件名的标题 */}
        <div className="absolute top-0 left-0 right-0 bg-black/5 dark:bg-white/5 p-2 z-10 flex items-center justify-between">
          <div className="text-sm font-medium truncate">{filename}</div>
          {onClick && (
            <button
              onClick={handleClick}
              className="p-1 rounded-full hover:bg-black/10 dark:hover:bg-white/10"
            >
              <ExternalLink size={14} />
            </button>
          )}
        </div>
      </div>
    );
  }

  // 带详情的普通文件
  const safeStyle = { ...customStyle };
  delete safeStyle.height;
  delete safeStyle['--attachment-height'];

  return (
    <button
      onClick={handleClick}
      className={cn(
        'group flex rounded-xl transition-all duration-200 min-h-[54px] h-[54px] overflow-hidden cursor-pointer',
        'border border-black/10 dark:border-white/10',
        'bg-sidebar',
        'text-left',
        'pr-7', // 右侧内边距用于 X 按钮
        isInlineMode
          ? 'min-w-[170px] w-full sm:max-w-[300px] sm:w-fit' // 移动端占满宽度，大屏幕受限
          : 'min-w-[170px] max-w-[300px] w-fit', // 网格布局的原始约束
        className,
      )}
      style={safeStyle}
      title={filename}
    >
      <div className="relative min-w-[54px] w-[54px] h-full aspect-square flex-shrink-0 bg-black/5 dark:bg-white/5">
        <div className="flex items-center justify-center h-full w-full">
          <IconComponent className="h-5 w-5 text-black/60 dark:text-white/60" />
        </div>
      </div>

      <div className="flex-1 min-w-0 flex flex-col justify-center p-2 pl-3 overflow-hidden">
        <div className="text-sm font-medium text-foreground truncate max-w-full">
          {filename}
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-1 truncate">
          <span className="text-black/60 dark:text-white/60 truncate">
            {typeLabel}
          </span>
          <span className="text-black/40 dark:text-white/40 flex-shrink-0">
            ·
          </span>
          <span className="text-black/60 dark:text-white/60 flex-shrink-0">
            {fileSize}
          </span>
        </div>
      </div>
    </button>
  );
}

interface FileAttachmentGridProps {
  attachments: string[];
  onFileClick?: (path: string, filePathList?: string[]) => void;
  className?: string;
  sandboxId?: string;
  showPreviews?: boolean;
  collapsed?: boolean;
  project?: Project;
}

export function FileAttachmentGrid({
  attachments,
  onFileClick,
  className,
  sandboxId,
  showPreviews = true,
  collapsed = false,
  project,
}: FileAttachmentGridProps) {
  if (!attachments || attachments.length === 0) return null;

  return (
    <AttachmentGroup
      files={attachments}
      onFileClick={onFileClick}
      className={className}
      sandboxId={sandboxId}
      showPreviews={showPreviews}
      layout="grid"
      gridImageHeight={150} // 网格布局使用更大的高度
      collapsed={collapsed}
      project={project}
    />
  );
}
