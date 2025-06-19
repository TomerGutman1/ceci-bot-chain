export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      israeli_government_decisions: {
        Row: {
          all_tags: string | null
          committee: string | null
          created_at: string | null
          decision_content: string | null
          decision_date: string | null
          decision_key: string | null
          decision_number: string | null
          decision_title: string | null
          decision_url: string | null
          embedding: string | null
          government_number: string | null
          id: number
          operativity: string | null
          prime_minister: string | null
          summary: string | null
          tags_government_body: string | null
          tags_location: string | null
          tags_policy_area: string | null
          updated_at: string | null
        }
        Insert: {
          all_tags?: string | null
          committee?: string | null
          created_at?: string | null
          decision_content?: string | null
          decision_date?: string | null
          decision_key?: string | null
          decision_number?: string | null
          decision_title?: string | null
          decision_url?: string | null
          embedding?: string | null
          government_number?: string | null
          id?: number
          operativity?: string | null
          prime_minister?: string | null
          summary?: string | null
          tags_government_body?: string | null
          tags_location?: string | null
          tags_policy_area?: string | null
          updated_at?: string | null
        }
        Update: {
          all_tags?: string | null
          committee?: string | null
          created_at?: string | null
          decision_content?: string | null
          decision_date?: string | null
          decision_key?: string | null
          decision_number?: string | null
          decision_title?: string | null
          decision_url?: string | null
          embedding?: string | null
          government_number?: string | null
          id?: number
          operativity?: string | null
          prime_minister?: string | null
          summary?: string | null
          tags_government_body?: string | null
          tags_location?: string | null
          tags_policy_area?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      get_decisions_stats: {
        Args: Record<PropertyKey, never>
        Returns: {
          total_decisions: number
          total_committees: number
          total_with_content: number
          total_with_url: number
        }[]
      }
      get_filter_options: {
        Args: Record<PropertyKey, never>
        Returns: {
          committees: string[]
          policy_areas: string[]
          government_bodies: string[]
          locations: string[]
        }[]
      }
      import_csv_data: {
        Args: {
          p_committee: string
          p_decision_title: string
          p_decision_content: string
          p_decision_url: string
          p_operativity: string
          p_tags_policy_area: string
          p_tags_government_body: string
          p_tags_location: string
          p_all_tags: string
          p_decision_key: string
          p_embedding?: string
        }
        Returns: undefined
      }
      search_decisions: {
        Args: {
          search_term?: string
          committee_filter?: string
          policy_area_filter?: string
          location_filter?: string
          limit_results?: number
        }
        Returns: {
          id: number
          committee: string
          decision_title: string
          decision_content: string
          decision_url: string
          operativity: string
          tags_policy_area: string
          tags_government_body: string
          tags_location: string
          all_tags: string
          decision_key: string
          rank: number
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
