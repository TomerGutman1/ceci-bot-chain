export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
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
      current_government: {
        Row: {
          gov: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      count_all_decisions: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
        }[]
      }
      count_decisions_by_government: {
        Args: { gov_number: number }
        Returns: {
          count: number
        }[]
      }
      count_decisions_by_government_and_topic: {
        Args: { gov_number: number; topic_name: string }
        Returns: {
          count: number
          topic: string
          government_number: string
          prime_minister: string
        }[]
      }
      count_decisions_by_topic: {
        Args: { topic_name: string }
        Returns: {
          count: number
        }[]
      }
      count_decisions_by_year: {
        Args: { target_year: number }
        Returns: {
          count: number
        }[]
      }
      count_decisions_per_government: {
        Args: Record<PropertyKey, never>
        Returns: {
          government_number: string
          prime_minister: string
          count: number
          first_decision: string
          last_decision: string
        }[]
      }
      current_gov_decisions_by_topic: {
        Args: { p_topic: string; p_limit?: number }
        Returns: {
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
        }[]
      }
      execute_simple_sql: {
        Args: { query: string }
        Returns: {
          result: Json
        }[]
      }
      execute_sql: {
        Args: { query_text: string; params?: Json }
        Returns: Json
      }
      get_all_decisions: {
        Args: Record<PropertyKey, never>
        Returns: {
          id: number
          decision_date: string
          decision_number: string
          committee: string
          decision_title: string
          decision_content: string
          decision_url: string
          summary: string
          operativity: string
          tags_policy_area: string
          tags_government_body: string
          tags_location: string
          all_tags: string
          government_number: number
          prime_minister: string
          decision_key: string
          created_at: string
          updated_at: string
        }[]
      }
      get_decisions_by_date_range: {
        Args: { start_date: string; end_date: string }
        Returns: {
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
        }[]
      }
      get_decisions_by_government_and_topic: {
        Args: { gov_number: string; topic_name: string }
        Returns: {
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
        }[]
      }
      get_decisions_by_prime_minister: {
        Args: { pm_name: string }
        Returns: {
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
        }[]
      }
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
      get_government_statistics: {
        Args: { gov_number: number }
        Returns: {
          government_number: string
          decision_count: number
          prime_minister: string
          first_decision: string
          last_decision: string
          policy_areas_count: number
        }[]
      }
      get_important_decisions_by_year: {
        Args: { target_year: number }
        Returns: {
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
      search_decisions_content: {
        Args: { search_term: string }
        Returns: {
          decision_key: string
          decision_number: string
          government_number: string
          decision_title: string
          decision_date: string
          tags_policy_area: string
          decision_url: string
          relevance: number
        }[]
      }
      search_decisions_hebrew: {
        Args: { search_term: string }
        Returns: {
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

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
