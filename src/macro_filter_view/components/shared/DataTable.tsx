/**
 * Advanced Data Table Component
 * Sortable, filterable table with inline actions and Hebrew RTL support
 */

import React, { useState, useMemo } from 'react';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table';
import { 
  ChevronDown, 
  ChevronUp, 
  ArrowUpDown,
  Search,
  ExternalLink,
  Download,
  Eye
} from 'lucide-react';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { formatHebrewDate, formatHebrewNumber } from '../../utils/dataTransformers';
import type { DashboardDecision } from '../../types/decision';

interface DataTableProps {
  data: DashboardDecision[];
  loading?: boolean;
  onViewDecision?: (decision: DashboardDecision) => void;
  onExportData?: () => void;
  className?: string;
}

export default function DataTable({
  data,
  loading = false,
  onViewDecision,
  onExportData,
  className,
}: DataTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [pageSize, setPageSize] = useState(25);

  // Table columns definition
  const columns = useMemo<ColumnDef<DashboardDecision>[]>(
    () => [
      {
        accessorKey: 'number',
        header: 'מס׳ החלטה',
        cell: ({ row }) => (
          <div className="font-medium">
            <div>{row.original.number}</div>
            <div className="text-xs text-gray-500">
              ממשלה {row.original.government}
            </div>
          </div>
        ),
        size: 100,
      },
      {
        accessorKey: 'title',
        header: 'כותרת ההחלטה',
        cell: ({ row }) => (
          <div className="max-w-md">
            <div className="font-medium line-clamp-2 text-right">
              {row.original.title}
            </div>
            <div className="text-xs text-gray-500 mt-1 line-clamp-1">
              {row.original.summary}
            </div>
          </div>
        ),
        size: 400,
      },
      {
        accessorKey: 'date',
        header: 'תאריך',
        cell: ({ row }) => (
          <div className="text-sm">
            {formatHebrewDate(row.original.date)}
          </div>
        ),
        size: 120,
      },
      {
        accessorKey: 'type',
        header: 'סוג',
        cell: ({ row }) => (
          <Badge
            variant="secondary"
            className={cn(
              'text-xs',
              row.original.type === 'אופרטיבית'
                ? 'bg-green-100 text-green-800'
                : 'bg-blue-100 text-blue-800'
            )}
          >
            {row.original.type}
          </Badge>
        ),
        size: 100,
      },
      {
        accessorKey: 'committee',
        header: 'ועדה',
        cell: ({ row }) => (
          <div className="text-sm max-w-xs truncate">
            {row.original.committee || 'לא צוין'}
          </div>
        ),
        size: 150,
      },
      {
        accessorKey: 'policyAreas',
        header: 'תחומי מדיניות',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1 max-w-xs">
            {row.original.policyAreas.slice(0, 2).map((area, index) => (
              <Badge
                key={index}
                variant="outline"
                className="text-xs"
              >
                {area}
              </Badge>
            ))}
            {row.original.policyAreas.length > 2 && (
              <Badge variant="outline" className="text-xs">
                +{row.original.policyAreas.length - 2}
              </Badge>
            )}
          </div>
        ),
        size: 200,
      },
      {
        accessorKey: 'primeMinister',
        header: 'ראש ממשלה',
        cell: ({ row }) => (
          <div className="text-sm">
            {row.original.primeMinister}
          </div>
        ),
        size: 120,
      },
      {
        id: 'actions',
        header: 'פעולות',
        cell: ({ row }) => (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onViewDecision?.(row.original)}
              className="h-8 w-8 p-0"
            >
              <Eye className="h-4 w-4" />
              <span className="sr-only">הצג פרטים</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(row.original.url, '_blank')}
              className="h-8 w-8 p-0"
            >
              <ExternalLink className="h-4 w-4" />
              <span className="sr-only">פתח קישור</span>
            </Button>
          </div>
        ),
        size: 100,
        enableSorting: false,
      },
    ],
    [onViewDecision]
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      globalFilter,
      pagination: {
        pageIndex: 0,
        pageSize,
      },
    },
    initialState: {
      pagination: {
        pageSize,
      },
    },
  });

  const getSortIcon = (isSorted: false | 'asc' | 'desc') => {
    if (isSorted === 'asc') return <ChevronUp className="h-4 w-4" />;
    if (isSorted === 'desc') return <ChevronDown className="h-4 w-4" />;
    return <ArrowUpDown className="h-4 w-4 opacity-50" />;
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Table Controls */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="חיפוש בטבלה..."
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="w-64 pr-10 text-right"
            />
          </div>
          
          <Select
            value={pageSize.toString()}
            onValueChange={(value) => {
              setPageSize(parseInt(value));
              table.setPageSize(parseInt(value));
            }}
          >
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-sm text-gray-500">
            {formatHebrewNumber(table.getFilteredRowModel().rows.length)} תוצאות
          </div>
          
          {onExportData && (
            <Button variant="outline" size="sm" onClick={onExportData}>
              <Download className="h-4 w-4 mr-2" />
              ייצוא
            </Button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className="text-right"
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={cn(
                          'flex items-center gap-2',
                          header.column.getCanSort() && 'cursor-pointer select-none hover:bg-gray-50 p-2 -m-2 rounded'
                        )}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {header.column.getCanSort() && (
                          getSortIcon(header.column.getIsSorted())
                        )}
                      </div>
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          
          <TableBody>
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  {columns.map((_, colIndex) => (
                    <TableCell key={colIndex}>
                      <div className="h-4 bg-gray-200 rounded animate-pulse" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="hover:bg-gray-50"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="py-3">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-gray-500"
                >
                  לא נמצאו תוצאות
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            עמוד {table.getState().pagination.pageIndex + 1} מתוך{' '}
            {table.getPageCount()}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              הקודם
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              הבא
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}